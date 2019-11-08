from rest_framework import generics, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model
from CustomUsers.models import UserDetailModel, UserOTPModel
from CustomUsers.serializers import (UserAuthSerializer, UserFCMKeySerializer, OTPVerificationSerializer,
                                     UserDetailBasicSerializer, UserIsAgreedSerializer, UserDetailAddressSerializer)
from CustomUsers.scripts import OTPManager, UserInformationCheck
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
        result['message'] = OTPManager().check_user_inputed_otp(int(request.data['otp_number']), self.kwargs['pk'])
        if result['message'] == 'otp matched':
            result['tokens'] = self.get_tokens_for_user(get_user_model().objects.get(id=self.kwargs['pk']))
        else:
            result['tokens'] = ''
        result['user_detail'] = UserInformationCheck().is_user_detail_exists(self.kwargs['pk'])
        result['product_category'] = "0"
        result['is_agree'] = UserInformationCheck().is_user_agreed(self.kwargs['pk'], result['user_detail'])
        result['address_info'] = UserInformationCheck().is_address_exists(self.kwargs['pk'], result['user_detail'])
        result['is_verified'] = UserInformationCheck().is_user_verified(self.kwargs['pk'], result['user_detail'])
        return Response(result)


class UserDetailBasicCreateView(generics.CreateAPIView):
    queryset = UserDetailModel
    serializer_class = UserDetailBasicSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['user_id'] = request.user.id
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception:
            return Response({'result': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED, headers=None)


class UserIsAgreedUpdateView(generics.UpdateAPIView):
    queryset = UserDetailModel
    serializer_class = UserIsAgreedSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = get_object_or_404(self.queryset, user=get_user_model().objects.get(Q(id=self.request.user.id) & Q(is_active=True)))
        super().check_object_permissions(self.request, obj)
        return obj


class UserDetailAddressUpdateView(generics.UpdateAPIView):
    queryset = UserDetailModel
    serializer_class = UserDetailAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = get_object_or_404(self.queryset, user=get_user_model().objects.get(Q(id=self.request.user.id) & Q(is_active=True)))
        super().check_object_permissions(self.request, obj)
        return obj
