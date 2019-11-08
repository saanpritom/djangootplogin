from rest_framework import generics, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from django.contrib.auth import get_user_model
from CustomUsers.models import UserOTPModel
from CustomUsers.serializers import UserAuthSerializer, UserFCMKeySerializer, OTPVerificationSerializer
from CustomUsers.scripts import OTPManager
from CustomUsers.permissions import IsUserExists
from CustomUsers.tasks import initialize_otp_and_sms_otp


# Create your views here.
class UserAuthAPIView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserAuthSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        result = serializer.is_valid(raise_exception=True)
        try:
            if result == 'exists':
                headers = None
                response_text = get_user_model().objects.get(mobile=request.data['mobile']).id
            else:
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                response_text = get_user_model().objects.get(mobile=request.data['mobile']).id
            return Response({'result': response_text}, status=status.HTTP_201_CREATED, headers=headers)
        except Exception:
            return Response({'result': 'error'}, status=status.HTTP_406_NOT_ACCEPTABLE, headers=None)


class UserFCMKeyView(generics.UpdateAPIView):
    queryset = get_user_model()
    serializer_class = UserFCMKeySerializer
    permission_classes = [IsUserExists]

    def perform_update(self, serializer):
        super().perform_update(serializer)
        initialize_otp_and_sms_otp.delay(self.kwargs['pk'])


class UserOTPVerificationView(generics.UpdateAPIView):
    queryset = UserOTPModel
    serializer_class = OTPVerificationSerializer
    permission_classes = [IsUserExists]

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def get_object(self):
        obj = self.queryset.objects.filter(Q(user=get_user_model().objects.get(id=self.kwargs['pk'])) & Q(is_active=True))
        return obj

    def update(self, request, *args, **kwargs):
        result = {}
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        result['otp_status'] = OTPManager().check_user_inputed_otp(int(request.data['otp_number']), self.kwargs['pk'])
        if result['otp_status'] == 'otp matched':
            result['tokens'] = self.get_tokens_for_user(get_user_model().objects.get(id=self.kwargs['pk']))
        else:
            result['tokens'] = ''
        return Response(result)
