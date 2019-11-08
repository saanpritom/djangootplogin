from rest_framework import serializers
from CustomUsers.models import UserAuthModel, UserDetailModel, UserOTPModel


class UserAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAuthModel
        fields = ['mobile']

    def is_valid(self, raise_exception=True):
        if self.initial_data is not None:
            # check if the inputed mobile number is existed or not
            if self.Meta().model.objects.filter(mobile=self.initial_data['mobile']).count() > 0:
                return 'exists'
            else:
                return super(UserAuthSerializer, self).is_valid()


class UserFCMKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAuthModel
        fields = ['fcm_key']


class OTPVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOTPModel
        fields = ['otp_number']


class UserDetailBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetailModel
        fields = ['user', 'name', 'date_of_birth', 'nid_number', 'gender']
