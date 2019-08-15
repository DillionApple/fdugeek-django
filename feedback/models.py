from django.db import models

# Create your models here.
class Feedback(models.Model):

    feedback = models.CharField(max_length=512)
    contact_email = models.CharField(max_length=128, null=True)
    create_time = models.DateTimeField(auto_created=True, null=True)

    def __str__(self):
        return self.feedback[:50]