from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid


# Create your models here.
class UserGroupModel(models.Model):
    name = models.CharField(max_length=80, unique=True, null=False, blank=False, verbose_name='Group Name')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UserAuthModelManager(BaseUserManager):

    def create_user(self, mobile, group):
        user = self.model(mobile=mobile, group=group)
        user.save()
        return user

    def create_superuser(self, mobile, password=None):
        group = UserGroupModel.objects.get(name='Admin')
        user = self.create_user(mobile, group)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class UserAuthModel(AbstractUser):
    group = models.ForeignKey(UserGroupModel, related_name='user_group', on_delete=models.CASCADE, null=False, default=2)
    username = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    mobile = models.CharField(max_length=11, unique=True, null=False, blank=False, verbose_name='Mobile Number')
    fcm_key = models.CharField(max_length=80, null=False, blank=False, default='0')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'mobile'

    objects = UserAuthModelManager()

    def __str__(self):
        return self.mobile


class UserDetailModel(models.Model):
    user = models.OneToOneField(UserAuthModel, related_name='user_detail', on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=80, null=False, blank=False, verbose_name='Name')
    date_of_birth = models.DateField(null=False, blank=False, verbose_name='Date of Birth')
    nid_number = models.CharField(max_length=40, unique=True, null=False, blank=False, verbose_name='NID Number', default='0')
    gender = models.CharField(max_length=80, null=True, blank=True, verbose_name='Gender')
    area = models.CharField(max_length=80, null=False, blank=False, verbose_name='Area')
    address = models.TextField(null=False, blank=False, verbose_name='Address', default='TON618')
    fb_page_link = models.URLField(null=True, blank=True, verbose_name='Facebook Page Link')
    instagram_link = models.URLField(null=True, blank=True, verbose_name='Instagram Page Link')
    image = models.ImageField(upload_to='users/%Y/%m/%d/', default='users/defaults/user.png', verbose_name='Profile Picture')
    is_verified = models.BooleanField(default=False)
    is_agreed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
