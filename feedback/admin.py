from django.contrib import admin

# Register your models here.

from feedback.models import Feedback

admin.site.register(Feedback)