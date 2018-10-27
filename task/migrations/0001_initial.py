# Generated by Django 2.1.2 on 2018-10-04 12:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application_time', models.DateTimeField(auto_created=True)),
                ('application_text', models.CharField(max_length=4096)),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='account.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_created=True)),
                ('title', models.CharField(max_length=128)),
                ('description', models.CharField(max_length=4096)),
                ('type', models.CharField(choices=[('build_group', '开发团队招募'), ('programing', '开发任务'), ('tutor', '家教')], max_length=32)),
                ('due_time', models.DateTimeField()),
                ('reward', models.TextField(max_length=512)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.Account')),
            ],
        ),
        migrations.AddField(
            model_name='application',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='task.Task'),
        ),
    ]
