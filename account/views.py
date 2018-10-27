import json
import time

from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from account.models import Account
from account.utils import get_user_private_dict
from account.decorators import login_required
from utils.api_utils import get_json_dict
from utils.util_functions import get_md5, check_fdu_auth

@require_POST
def user_login(request):
    request.POST = json.loads(request.body.decode('utf-8'))
    username = request.POST['username']
    password = request.POST['password']

    json_dict = {
        'err_code': 0,
        'message': "Login success",
        'data': {},
    }

    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist as e:
        user = None

    if user == None: # login for the first time, not registered
        user_email_name = check_fdu_auth(username, password)
        if user_email_name != None:
            user = User(username=username)
            user.set_password(password)
            user.save()
            account = Account(user=user)
            account.nickname = user_email_name
            account.save()

    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        return JsonResponse(json_dict)
    else:
        json_dict['err_code'] = -1
        json_dict['message'] = "用户名或密码错误"
        return JsonResponse(json_dict)


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
    
