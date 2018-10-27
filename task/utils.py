from django.utils import timezone

from account.utils import get_user_public_dict

def get_task_dict(task):
    #[TODO] check state every night(00:00), not every time request the task

    if (task.state == "active"):
        due_time = timezone.localtime(task.due_time)
        now_time = timezone.now()
        if (now_time >= due_time):
            task.state = "finished"
            task.save()

    ret = {}
    ret["task_id"] = task.id
    ret["title"] = task.title
    ret["description"] = task.description
    ret["requirement"] = task.requirement
    ret["type"] = task.type
    ret["state"] = task.state
    ret["create_time"] = timezone.localtime(task.create_time).strftime("%Y-%m-%d %H:%M")
    ret["due_time"] = timezone.localtime(task.due_time).strftime("%Y-%m-%d %H:%M")
    ret["reward"] = task.reward
    ret["creator"] = get_user_public_dict(task.creator)
    ret["application_count"] = task.applications.count()

    return ret

def get_application_dict(application):
    return {
        "applicant": get_user_public_dict(application.applicant),
        "task": get_task_dict(application.task),
        "application_time": timezone.localtime(application.application_time).strftime("%Y-%m-%d %H:%M"),
        "application_text": application.application_text
    }

def get_comment_dict(comment):
    return {
        "comment_id": comment.id,
        "account": get_user_public_dict(comment.account),
        "task": get_task_dict(comment.task),
        "create_time": timezone.localtime(comment.create_time).strftime("%Y-%m-%d %H:%M"),
        "content": comment.content,
    }