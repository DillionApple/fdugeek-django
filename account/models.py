from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Account(models.Model):

    def user_icon_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<username>/icons/<filename>
        return 'user_{0}/icons/{1}'.format(instance.user.username, filename)

    GENDERS = (("M", "Male"), ("F", "Female"), ("U", "Unknown"))

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=16, choices=GENDERS, default="U")
    nickname = models.CharField(max_length=32)
    school = models.CharField(max_length=64, null=True)
    major = models.CharField(max_length=64, null=True)
    mobile_phone = models.CharField(max_length=32, null=True)
    wechat = models.CharField(max_length=32, null=True)
    qq = models.CharField(max_length=32, null=True)
    icon = models.ImageField(
        upload_to=user_icon_path,
        default="default_pictures/male-default.png"
    )

    def __str__(self):
        return self.user.username

class AccountConfirmCode(models.Model):

    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="account_confirm_code")
    code = models.CharField(max_length=128, default="")
    update_time = models.DateTimeField(auto_now=True)