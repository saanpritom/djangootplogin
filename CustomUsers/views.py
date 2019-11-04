from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from CustomUsers.serializers import UserAuthSerializer
from CustomUsers.scripts import OTPManager


# Create your views here.
class UserAuthAPIView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserAuthSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        result = serializer.is_valid(raise_exception=True)
        if result == 'exists':
            headers = None
            otp = OTPManager().initialize_otp(get_user_model().objects.get(mobile=serializer.initial_data['mobile']).id)
        else:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            otp = OTPManager().initialize_otp(get_user_model().objects.get(mobile=serializer.initial_data['mobile']).id)
        return Response({'otp': otp}, status=status.HTTP_201_CREATED, headers=headers)
