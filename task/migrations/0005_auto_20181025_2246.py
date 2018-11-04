# Generated by Django 2.1.2 on 2018-10-25 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0004_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='state',
            field=models.CharField(choices=[('active', '招募中'), ('time_over', '报名截止'), ('finished', '已完成 ')], default='active', max_length=32),
        ),
        migrations.AlterField(
            model_name='task',
            name='type',
            field=models.CharField(choices=[('build_group', '开发团队招募'), ('programing', '开发任务'), ('tutor', '家教'), ('others', '其它')], max_length=32),
        ),
    ]