from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from CustomUsers.serializers import UserAuthSerializer, UserFCMKeySerializer
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
