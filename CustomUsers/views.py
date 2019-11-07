from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.contrib.auth import get_user_model
from CustomUsers.models import UserOTPModel
from CustomUsers.serializers import UserAuthSerializer, UserFCMKeySerializer, OTPVerificationSerializer
from CustomUsers.scripts import OTPManager
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
    permission_classes = [AllowAny]

    def perform_update(self, serializer):
        super().perform_update(serializer)
        initialize_otp_and_sms_otp.delay(self.kwargs['pk'])


class UserOTPVerificationView(generics.UpdateAPIView):
    queryset = UserOTPModel
    serializer_class = OTPVerificationSerializer
    permission_classes = [AllowAny]

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
            result['access'] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNDU2LCJqdGkiOiJmZDJmOWQ1ZTFhN2M0MmU4OTQ5MzVlMzYyYmNhOGJjYSJ9.NHlztMGER7UADHZJlxNG0WSi22a2KaYSfd1S-AuT7lU"
            result['refresh'] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNDU2LCJqdGkiOiJmZDJmOWQ1ZTFhN2M0MmU4OTQ5MzVlMzYyYmNhOGJjYSJ9.NHlztMGER7UADHZJlxNG0WSi22a2KaYSfd1S-AuT7lU"
        else:
            result['access'] = ''
            result['refresh'] = ''
        return Response(result)
