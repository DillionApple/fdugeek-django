from django.db import models
from django.contrib.auth.models import User

class Picture(models.Model):

    def user_pictures_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/pictures/user_<username>/<filename>
        return 'user_{0}/pictures/{1}'.format(instance.user.username, filename)

    picture = models.ImageField(upload_to=user_pictures_path)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.picture.url
