from django.db import models

# Create your models here.
class Feedback(models.Model):

    feedback = models.CharField(max_length=500)

    def __str__(self):
        return self.feedback[:50]