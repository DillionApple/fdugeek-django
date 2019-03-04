import json
import time
import requests
import jwt
import re

from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.core.files.base import ContentFile

from account.models import Account, AccountConfirmCode
from account.utils import *
from account.decorators import login_required
from account.keys import PRIVATE_KEY, PUBLIC_KEY
from utils.api_utils import get_json_dict
from utils.util_functions import get_md5

@require_GET
def get_public_key(request):

    return HttpResponse(PUBLIC_KEY)


@require_POST
def user_login(request):

    def get_user_login_success_response(user):
        expires = timezone.now() + timezone.timedelta(days=7)
        jwt_payload = get_user_private_dict(user.account)
        jwt_payload['expires'] = expires.strftime("%Y-%m-%d %H:%M:%S")
        jwt_token = jwt.encode(jwt_payload, PRIVATE_KEY, algorithm="RS256").decode("utf-8")
        response = JsonResponse(get_json_dict(data={}, err_code=0, message="Login success"))
        response.set_cookie('jwt', jwt_token, max_age=604800)
        return response

    received_data = json.loads(request.body.decode('utf-8'))
    username = received_data['username']
    password = received_data['password']

    json_dict = get_json_dict(data={})

    user = authenticate(username=username, password=password)
    if user: # user auth success
        if user.is_active: # user have confirmed its email, login success

            response = get_user_login_success_response(user)
            return response

        else: # user have not confirmed its email
            json_dict['err_code'] = -1
            json_dict['message'] = "请验证您的学号邮箱"
            response = JsonResponse(json_dict)
            response.status_code = 403
            return response
    else: # user auth fail
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist as e: # user object does not exist
            if (re.match("\d{3,11}", username)): # username is the form of a student/staff account
                nickname = check_fdu_auth(username, password) # check username and password via mail.fudan.edu.cn
                if nickname != None: # check success, create user
                    user = User(username=username)
                    user.set_password(password)
                    user.is_active = True
                    user.save()
                    account = Account(user=user)
                    account.nickname = nickname
                    account.save()
                    user_icon_response = requests.get("https://www.gravatar.com/avatar/{0}?s=256&d=identicon&r=PG".format(user.username))
                    account.icon.save(name='default_icon', content=ContentFile(user_icon_response.content))
                    return get_user_login_success_response(user)
            # user does not exists
            json_dict['err_code'] = -1
            json_dict['message'] = "用户不存在"
            response = JsonResponse(json_dict)
            response.status_code = 403
            return response
        else: # user exists, password is incorrect
            json_dict['err_code'] = -1
            json_dict['message'] = "密码错误"
            response = JsonResponse(json_dict)
            response.status_code = 403
            return response

@login_required
def refresh_token(request):

    jwt_payload = request.jwt_payload
    jwt_payload['expires'] = (timezone.now() + timezone.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")

    jwt_token = jwt.encode(jwt_payload, PRIVATE_KEY, algorithm="RS256").decode("utf-8")

    json_dict = get_json_dict(data={}, err_code=0, message="Refresh jwt token success")

    response = JsonResponse(json_dict)
    response.set_cookie('jwt', jwt_token, max_age=604800)
    return response

@require_POST
def register(request):

    request_data = json.loads(request.body.decode('utf-8'))
    username = request_data['username']
    password = request_data['password']

    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist as e:

        if not safe_password(password):
            return JsonResponse(get_json_dict(data={}, err_code=-1, message="密码不安全，请设置6-20位包含大写字母，小写字母，数字和特殊字符中至少两种的密码"),
                                status=403)

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

        if not safe_password(password):
            return JsonResponse(get_json_dict(data={}, err_code=-1, message="密码不安全，请设置6-20位包含大写字母，小写字母，数字和特殊字符中至少两种的密码"),
                                status=403)

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
        return HttpResponse("<h3>验证成功</h3>", status=200)
        # return JsonResponse(get_json_dict(data={}, err_code=0, message="验证成功，请前往登录"))
    else:
        return HttpResponse("<h3>验证出现问题</h3>", status=403)
        #return JsonResponse(get_json_dict(data={}, err_code=-1, message="验证出现问题"))

@login_required
@require_GET
def user_logout(request):
    json_dict = get_json_dict(data={}, err_code=0, message="Logout success")

    response = JsonResponse(json_dict)
    response.delete_cookie('jwt')
    return response

@login_required
@require_GET
def user_detail(request):
    account = request.user.account
    json_dict = get_json_dict(data={})

    json_dict['data'] = get_user_private_dict(account)

    return JsonResponse(json_dict)

@login_required
@require_GET
def get_user_public_detail(request):
    username = request.GET['username']

    account = Account.objects.get(user__username=username)

    json_dict = get_json_dict(data={})
    json_dict['data'] = get_user_public_dict(account)

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

        if not safe_password(new_password):
            return JsonResponse(get_json_dict(data={}, err_code=-1, message="密码不安全，请设置6-20位包含大写字母，小写字母，数字和特殊字符中至少两种的密码"),
                                status=403)

        user.set_password(new_password)
        user.save()
        login(request, user)
        return JsonResponse(get_json_dict(data={}))
    else:
        response = JsonResponse(get_json_dict(err_code=-1, message="密码错误", data={}))
        response.status_code = 403
        return response


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