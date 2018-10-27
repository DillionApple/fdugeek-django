import json

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone

from task.models import Task, Application, Comment
from task.utils import get_task_dict, get_application_dict, get_comment_dict
from utils.api_utils import get_json_dict, get_permission_denied_json_dict
from account.decorators import login_required

@require_GET
@login_required
def get_task_list(request):

    PAGE_SIZE = 20

    try:
        page = int(request.GET.get("page", 0))
    except:
        page = 0

    task_type = request.GET.get("task_type", "all")
    task_state = request.GET.get("task_state", "all")
    search_keyword = request.GET.get("search_keyword", "")

    st_task_index = PAGE_SIZE * page
    en_task_index = PAGE_SIZE * (page + 1)
    json_dict_data = {}

    json_dict_data["task_list"] = []

    tasks = Task.objects.all()
    if (task_type != "all"):
        tasks = tasks.filter(type=task_type)
    if (task_state != "all"):
        tasks = tasks.filter(state=task_state)
    if (search_keyword != ""):
        tasks = tasks.filter(title__contains=search_keyword)

    tasks = tasks.order_by("-create_time")[st_task_index:en_task_index]

    for task in tasks:
        json_dict_data["task_list"].append(get_task_dict(task))

    json_dict_data['task_count'] = Task.objects.count()

    return JsonResponse(get_json_dict(data=json_dict_data))

@require_GET
@login_required
def get_task(request):

    task_id = request.GET.get("task_id")
    task = Task.objects.get(id=task_id)

    json_dict_data = {"task": get_task_dict(task)}

    json_dict = get_json_dict(data=json_dict_data)

    return JsonResponse(json_dict)

@require_GET
@login_required
def get_user_applications(request):

    PAGE_SIZE = 10

    try:
        page  = int(request.GET.get("page", 0))
    except:
        page = 0

    index_st = PAGE_SIZE * page
    index_en = PAGE_SIZE * (page + 1)

    account = request.user.account
    applications = account.applications.order_by("-application_time")[index_st:index_en]

    json_dict = get_json_dict(data={"applications": []})

    for application in applications:
        json_dict["data"]["applications"].append(get_application_dict(application))

    return JsonResponse(json_dict)



@require_GET
@login_required
def get_published_tasks(request):

    PAGE_SIZE=10

    try:
        page = int(request.GET.get("page"))
    except:
        page = 0

    index_st = PAGE_SIZE * page
    index_en = PAGE_SIZE * (page + 1)


    account = request.user.account
    tasks = Task.objects.filter(creator=account)[index_st:index_en]

    json_dict = get_json_dict(data={"tasks": []})

    for task in tasks:
        json_dict["data"]["tasks"].append(get_task_dict(task))

    return JsonResponse(json_dict)


@require_GET
@login_required
def get_task_applications(request):

    task_id = request.GET.get("task_id")
    task = Task.objects.get(id=task_id)

    if (task.creator == request.user.account):

        json_dict = get_json_dict(data = {"applications": []})
        for application in task.applications.order_by("-application_time"):
            json_dict["data"]["applications"].append(get_application_dict(application))
        return JsonResponse(json_dict)
    else:
        return get_permission_denied_json_dict()


@require_POST
@login_required
def create_task(request):

    request_data = json.loads(request.body.decode('utf-8'))

    print(request_data)

    task = Task(
        title = request_data["title"],
        description = request_data["description"],
        requirement = request_data["requirement"],
        type = request_data["type"],
        reward = request_data["reward"],
        creator = request.user.account,
    )
    task.due_time = request_data["due_time"]

    task.save()

    task = Task.objects.get(id=task.id)

    json_dict_data = {'task': get_task_dict(task)}

    return JsonResponse(get_json_dict(data = json_dict_data))

@require_POST
@login_required
def delete_task(request):

    request_data = json.loads(request.body.decode('utf-8'))
    task_id = request_data.get("task_id")

    task = Task.objects.get(id = task_id)

    if task.creator.user.id == request.user.id:
        task.delete()
    else:
        return JsonResponse(get_permission_denied_json_dict())


    return JsonResponse(get_json_dict(data = {}))

@require_POST
@login_required
def change_task(request):

    request_data = json.loads(request.body.decode('utf-8'))

    print(request_data)

    task = Task.objects.get(id=request_data["task_id"])

    if task.creator.user.id == request.user.id:

        task.title = request_data["title"]
        task.description = request_data["description"]
        task.requirement = request_data["requirement"]
        task.type = request_data["type"]
        task.due_time = request_data["due_time"]
        task.reward = request_data["reward"]

        task.save()

        now_time = timezone.now()
        task = Task.objects.get(id=task.id)
        if (task.due_time >= now_time):
            task.state = 'active'
        else:
            task.state = 'finished'

        task.save()

    else:
        return JsonResponse(get_permission_denied_json_dict())

    return JsonResponse(get_json_dict(data={}))

@require_POST
@login_required
def finish_task(request):

    request_data = json.loads(request.body.decode('utf-8'))

    task = Task.objects.get(id=request_data['task_id'])

    if task.creator.user.id == request.user.id:
        task.state = 'finished'
        task.save()
        return JsonResponse(get_json_dict(data={}))
    else:
        return JsonResponse(get_permission_denied_json_dict())

@require_POST
@login_required
def apply_for_task(request):

    request_data = json.loads(request.body.decode('utf-8'))

    task = Task.objects.get(id=request_data["task_id"])

    if task.state == "finished":
        return JsonResponse(get_json_dict(data={}, err_code=-1, message="报名已截止，不再接受报名"))

    now_time = timezone.now()

    if now_time > task.due_time:
        task.state = "finished"
        task.save()
        return JsonResponse(get_json_dict(data={}, err_code=-1, message="报名已截止，不再接受报名"))

    applications = task.applications.filter(applicant=request.user.account)

    if len(applications) > 0:
        return JsonResponse(get_json_dict(data={}, err_code=-1, message="你已经报过名了哦"))

    application = Application(
        applicant = request.user.account,
        task = task,
        application_text=request_data["application_text"]
    )

    application.save()

    return JsonResponse(get_json_dict(data={}))


@require_POST
@login_required
def quit_task(request):

    request_data = json.loads(request.body.decode('utf-8'))

    task = Task.objects.get(id=request_data["task_id"])

    applications = task.applications.filter(applicant=request.user.account)

    if len(applications) == 0:
        return JsonResponse(get_json_dict(data={}, err_code=-1, message="你还没有申请过"))

    application = applications.first()
    application.delete()

    return JsonResponse(get_json_dict(data={}))

@require_POST
@login_required
def make_comment(request):

    request_data = json.loads(request.body.decode('utf-8'))

    account = request.user.account
    content = request_data['content']
    task_id = request_data['task_id']

    task = Task.objects.get(id=task_id)

    comment = Comment(account=account, task=task, content = content)

    comment.save()

    return JsonResponse(get_json_dict(data={}))


@require_GET
@login_required
def get_comments(request):

    task_id = int(request.GET.get('task_id'))

    page = int(request.GET.get('page', 0))

    PAGE_SIZE = 10

    index_st = PAGE_SIZE * page
    index_en = PAGE_SIZE * (page + 1)

    comments = Comment.objects.filter(task__id=task_id)[index_st:index_en]

    json_dict = get_json_dict(data={'comments': [], 'comment_count': Comment.objects.filter(task__id=task_id).count()})

    i = index_st

    for comment in comments:

        json_dict['data']['comments'].append(get_comment_dict(comment))
        json_dict['data']['comments'][-1]['index'] = i
        i += 1

    return JsonResponse(json_dict)


@require_GET
@login_required
def get_if_user_applied_task(request):

    task_id = int(request.GET.get("task_id"))

    task = Task.objects.get(id=task_id)

    try:
        application = task.applications.filter(applicant=request.user.account)[0]
    except:
        application = None

    applied = application != None
    if applied == True:
        application_dict = get_application_dict(application)
    else:
        application_dict = None

    return JsonResponse(get_json_dict(data={"applied": applied, "application": application_dict}))