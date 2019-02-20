from django.db import models

from account.models import Account

class Task(models.Model):

    TASK_TYPES = (("build_group", "开发团队招募"), ("programing", "开发任务"), ("knowledge_communication", "知识交流"), ("tutor", "家教"), ("others", "其它"))
    TASK_STATES = (("active", "招募中"), ("finished", "报名截止"))

    title = models.CharField(max_length=128)
    description = models.CharField(max_length=4096)
    requirement = models.CharField(max_length=4096, default="")
    type = models.CharField(max_length=32, choices=TASK_TYPES)
    state = models.CharField(max_length=32, choices=TASK_STATES, default="active")
    create_time = models.DateTimeField(auto_now_add=True)
    due_time = models.DateTimeField()
    reward = models.TextField(max_length=512)
    creator = models.ForeignKey(Account, on_delete=models.CASCADE)

class Application(models.Model):

    applicant = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="applications")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="applications")
    application_time = models.DateTimeField(auto_now_add=True)
    application_text = models.CharField(max_length=4096)

class Comment(models.Model):

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='comments')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    create_time = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=4096)