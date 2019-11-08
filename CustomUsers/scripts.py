# This class is responsible to create update and manage OTP codes

from random import randint
from datetime import datetime
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings
from CustomUsers.models import UserOTPModel, UserDetailModel
import pytz


class OTPManager(object):
    model = UserOTPModel

    def random_with_N_digits(self, max_length):
        range_start = 10**(max_length - 1)
        range_end = (10**max_length) - 1
        return randint(range_start, range_end)

    def get_otp_object(self, user_id):
        try:
            otp_object = self.model.objects.get(Q(user=get_user_model().objects.get(id=user_id)) & Q(is_active=True))
            return otp_object
        except Exception:
            return None

    def update_user_model(self, user_id):
        user_object = get_user_model().objects.get(id=user_id)
        user_object.is_partial_verified = True
        user_object.save()
        return None

    def create_otp(self, user_id):
        # generate unique OTP Number
        otp_number = self.generate_otp_number()
        otp_object = self.model(otp_number=otp_number, user=get_user_model().objects.get(id=user_id))
        otp_object.save()
        return otp_number

    def update_otp(self, user_id, matched_status):
        # get otp object
        otp_object = self.get_otp_object(user_id)
        if otp_object is not None:
            # increase one otp tried value
            otp_object.otp_tried = otp_object.otp_tried + 1
            # if matched_status is True then deactivate the OTP
            # if not then if the maximum limit exceeds deactivate the otp
            if matched_status == 'matched':
                otp_object.is_active = False
            elif matched_status == 'not_matched':
                if otp_object.otp_tried > 3:
                    otp_object.is_active = False
                else:
                    otp_object.is_active = True
            else:
                otp_object.is_active = False
            # update OTP model
            otp_object.save()
            # if matched_status is True then update the user to partially verified
            if matched_status == 'matched':
                self.update_user_model(otp_object.user.id)
            return None
        else:
            return None

    def check_otp_number_matched(self, otp_number):
        if self.model.objects.filter(otp_number=otp_number).count() > 0:
            return True
        else:
            return False

    def generate_otp_number(self):
        max_length = 6
        otp_number = self.random_with_N_digits(max_length)
        if self.check_otp_number_matched(otp_number):
            self.generate_otp_number()
        else:
            return otp_number

    def check_otp_activation(self, user_id):
        otp_object = self.get_otp_object(user_id)
        if otp_object is not None:
            return True
        else:
            return False

    def get_otp_try_remain(self, user_id):
        otp_object = self.get_otp_object(user_id)
        if otp_object is not None:
            return otp_object.otp_tried
        else:
            return 0

    def check_otp_max_try_remain(self, user_id):
        otp_object = self.get_otp_object(user_id)
        if otp_object is not None:
            if otp_object.otp_tried < 3:
                return True
            else:
                return False
        else:
            return False

    def is_otp_not_expired(self, otp_number):
        otp_object = self.model.objects.get(Q(otp_number=otp_number))
        diff_seconds = (datetime.now(pytz.timezone(settings.TIME_ZONE)) - otp_object.created_at).total_seconds()
        if diff_seconds < 58:
            return True
        else:
            return False

    def deactivate_user_otp(self, user_id):
        otp_object = self.get_otp_object(user_id)
        if otp_object is not None:
            otp_object.is_active = False
            otp_object.save()
        return None

    def initialize_otp(self, user_id):
        # check if the user already has OTP Created and that OTP is in active state
        if self.check_otp_activation(user_id):
            # if user previous OTP is active then at first deactivate it
            self.deactivate_user_otp(user_id)
            # save data to database
            otp_number = self.create_otp(user_id)
        else:
            # save data to database
            otp_number = self.create_otp(user_id)
        return otp_number

    def check_user_inputed_otp(self, otp_number, user_id):
        # get otp object
        otp_object = self.get_otp_object(user_id)
        if otp_object is not None:
            # check if otp expired
            if self.is_otp_not_expired(otp_object.otp_number):
                if self.check_otp_max_try_remain(user_id):
                    # check if otp is matched
                    if otp_object.otp_number == otp_number:
                        self.update_otp(otp_object.user.id, 'matched')
                        return 'otp matched'
                    else:
                        self.update_otp(otp_object.user.id, 'not_matched')
                        return 'otp not matched'
                else:
                    self.update_otp(otp_object.user.id, 'not_matched')
                    return 'limit out'
            else:
                self.update_otp(otp_object.user.id, 'expired')
                return 'expired'
        else:
            return 'limit out'


class UserInformationCheck(object):

    def is_user_detail_exists(self, user_id):
        if UserDetailModel.objects.filter(user=get_user_model().objects.get(Q(id=user_id) & Q(is_active=True))).count() > 0:
            return "1"
        else:
            return "0"

    def is_user_agreed(self, user_id, is_exists):
        if is_exists == "1":
            obj = UserDetailModel.objects.get(user=get_user_model().objects.get(Q(id=user_id) & Q(is_active=True)))
            if obj.is_agreed is True:
                return "1"
            else:
                return "0"
        else:
            return "0"

    def is_address_exists(self, user_id, is_exists):
        if is_exists == "1":
            obj = UserDetailModel.objects.get(user=get_user_model().objects.get(Q(id=user_id) & Q(is_active=True)))
            if obj.area != '' or obj.address != 'TON618':
                return "1"
            else:
                return "0"
        else:
            return "0"

    def is_user_verified(self, user_id, is_exists):
        if is_exists == "1":
            obj = UserDetailModel.objects.get(user=get_user_model().objects.get(Q(id=user_id) & Q(is_active=True)))
            if obj.is_verified is True:
                return "1"
            else:
                return "0"
        else:
            return "0"
