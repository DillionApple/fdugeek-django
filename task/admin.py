from django.contrib import admin

from task.models import Task, Application, Comment

admin.site.register(Task)
admin.site.register(Application)
admin.site.register(Comment)

