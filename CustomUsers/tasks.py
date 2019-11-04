# This file will be responsible for OTP verification and creation
from django.contrib.auth import get_user_model
from celery.utils.log import get_task_logger
from celery import shared_task
from CustomUsers.scripts import OTPManager
# from scripts.UtilityClasses.NotificationCycles.SharedTasks import send_sms_to_user_by_queue

logger = get_task_logger(__name__)


# This Task will create otp queue and send sms to user
@shared_task
def initialize_otp_and_sms_otp(user_id):
    otp_number = OTPManager().initialize_otp(user_id)
    if int(otp_number):
        user_object = get_user_model().objects.get(id=user_id)
        return user_object
        # smsText = 'Your verification number is ' + str(otp_number)
        # send_sms_to_user_by_queue.delay(smsText, user_object.contact_number, 'TEXT')
    else:
        pass
