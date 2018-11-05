import json
import time
import datetime
import requests

from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.core.files.base import ContentFile

from account.models import Account, AccountConfirmCode
from account.utils import get_user_private_dict, generate_account_confirm_code, send_confirm_code_to_fdu_mailbox
from account.decorators import login_required
from utils.api_utils import get_json_dict
from utils.util_functions import get_md5, check_fdu_auth


@require_POST
def user_login(request):
    request.POST = json.loads(request.body.decode('utf-8'))
    username = request.POST['username']
    password = request.POST['password']

    json_dict = get_json_dict(data={}, message="Login Success")

    user = authenticate(username=username, password=password)
    if user:
        if user.is_active:
            login(request, user)
            return JsonResponse(json_dict)
        else:
            json_dict['err_code'] = -1
            json_dict['message'] = "请验证您的学号邮箱"
            return JsonResponse(json_dict)
    else:
        json_dict['err_code'] = -1
        json_dict['message'] = "用户名或密码错误，或者请确认您已完成邮箱认证"
        return JsonResponse(json_dict)

@require_POST
def register(request):

    request_data = json.loads(request.body.decode('utf-8'))
    username = request_data['username']
    password = request_data['password']

    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist as e:
        user = User(username=username)
        user.set_password(password)
        user.is_active = False
        user.save()
        account = Account(user=user)
        account.nickname = username
        account.save()
        account_confirm_code = AccountConfirmCode(account=account, code=generate_account_confirm_code())
        account_confirm_code.save()
    else:
        if user.is_active:
            return JsonResponse(get_json_dict(data={}, err_code=-1, message="您已注册过"))
        user.set_password(password)
        user.save()
        account_confirm_code = user.account.account_confirm_code
        account_confirm_code.code = generate_account_confirm_code()
        account_confirm_code.save()

    send_confirm_code_to_fdu_mailbox(username, account_confirm_code.code)

    return JsonResponse(get_json_dict(data={}))

@require_GET
def confirm_register(request):

    confirm_code = request.GET['confirm_code']
    username = request.GET['username']

    user = User.objects.get(username=username)

    if user.is_active:
        return HttpResponse("<h3>您已激活，请直接登录</h3>")
        # return JsonResponse(get_json_dict(data={}, err_code=-1, message="您已激活"))

    thirty_minutes = timezone.timedelta(minutes=30)
    due_time = user.account.account_confirm_code.update_time + thirty_minutes
    now_time = timezone.now()


    if (now_time > due_time):
        return HttpResponse("<h3>验证链接过期，请重新注册<h3>")
        # return JsonResponse(get_json_dict(data={}, err_code=-1, message="验证链接过期，请重新注册"))

    if confirm_code == user.account.account_confirm_code.code:
        user.is_active = True
        user.save()
        user_icon_response = requests.get("https://www.gravatar.com/avatar/{0}?s=256&d=identicon&r=PG".format(user.username))
        user.account.icon.save(name='default_icon', content=ContentFile(user_icon_response.content))
        return HttpResponse("<h3>验证成功</h3>")
        # return JsonResponse(get_json_dict(data={}, err_code=0, message="验证成功，请前往登录"))
    else:
        return HttpResponse("<h3>验证出现问题</h3>")
        #return JsonResponse(get_json_dict(data={}, err_code=-1, message="验证出现问题"))

@login_required
@require_GET
def user_logout(request):
    logout(request)
    json_dict = {
        'err_code': 0,
        'message': "Logout success",
        'data': {}
    }

    return JsonResponse(json_dict)

@login_required
@require_GET
def user_detail(request):
    account = request.user.account
    json_dict = get_json_dict(data={})

    json_dict['data'] = get_user_private_dict(account)

    return JsonResponse(json_dict)

@login_required
@require_POST
def change_detail(request):
    received_data = json.loads(request.body.decode('utf-8'))
    new_nickname = received_data['nickname']
    new_gender = received_data['gender']
    new_school = received_data['school']
    new_major = received_data['major']
    new_mobile_phone = received_data['mobile_phone']
    new_wechat = received_data['wechat']
    new_qq = received_data['qq']

    account = request.user.account
    account.nickname = new_nickname
    account.gender = new_gender
    account.school = new_school
    account.major = new_major
    account.mobile_phone = new_mobile_phone
    account.wechat = new_wechat
    account.qq = new_qq
    account.save()

    return JsonResponse(get_json_dict(data={}))

@login_required
@require_POST
def change_password(request):
    received_data = json.loads(request.body.decode('utf-8'))
    old_password = received_data['old_password']
    new_password = received_data['new_password']

    user = authenticate(username=request.user.username, password=old_password)    
    if user:
        user.set_password(new_password)
        user.save()
        login(request, user)
        return JsonResponse(get_json_dict(data={}))
    else:
        return JsonResponse(get_json_dict(err_code=-1, message="密码错误", data={}))


@login_required
@require_POST
def change_icon(request):
    picture = request.FILES['picture']
    
    picture.name = "{timestamp}_{picture_name}".format(
        timestamp = int(round(time.time() * 1000)),
        picture_name = get_md5(picture.read())
    )

    account = request.user.account
    account.icon = picture
    account.save()

    return JsonResponse(get_json_dict(data={'icon': account.icon.url}))
    
