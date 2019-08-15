import jwt
from time import sleep

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from account.models import *

LOGIN_URL = "/account/login/"
REGISTER_URL = "/account/register/"
CONFIRM_REGISTER_URL = "/account/confirm_register/"
LOGOUT_URL = "/account/logout/"
DETAIL_URL = "/account/detail/"
PUBLIC_DETAIL_URL = "/account/public_detail/"
CHANGE_DETAIL_URL = "/account/change_detail/"
CHANGE_PASSWORD_URL = "/account/change_password/"
CHANGE_ICON_URL = "/account/change_icon/"
PUBLIC_KEY_URL = "/account/public_key/"
REFRESH_TOKEN_URL = "/account/refresh_token/"

PASSWORD = "safe_password"

class AccountTestCase(TestCase):

    public_key = None

    def setUp(self):
        c = Client()
        response = c.get(PUBLIC_KEY_URL)
        assert response.status_code == 200
        self.public_key = response.content

        user = User(username="user0")
        user.set_password(PASSWORD)
        user.save()
        account = Account(user=user, nickname="nickname0")
        account.save()

    # test functions:
    # register, confirm_register
    def test_register(self):

        c = Client()

        # start to register a new user with unsafe password
        unsafe_password = 'password'
        response = c.post(REGISTER_URL, {'username': 'new_user0', 'password': unsafe_password}, content_type="application/json")
        assert(response.status_code == 403)
        assert(response.json()['message'] == "密码不安全，请设置6-20位包含大写字母，小写字母，数字和特殊字符中至少两种的密码")

        # start to register a new user with safe password
        response = c.post(REGISTER_URL, {'username': 'new_user0', 'password': PASSWORD}, content_type="application/json")
        new_user0 = User.objects.get(username="new_user0")
        assert(new_user0.is_active == False)

        # confirm_code is wrong
        response = c.get(CONFIRM_REGISTER_URL,
                         {'confirm_code': "wrong_code",
                          'username': new_user0.username})
        assert(response.status_code == 403)
        new_user0.refresh_from_db()
        assert(new_user0.is_active == False)

        # confirm_code is right
        response = c.get(CONFIRM_REGISTER_URL, {
            'confirm_code': new_user0.account.account_confirm_code.code,
            'username': new_user0.username
        })
        assert(response.status_code == 200)
        new_user0.refresh_from_db()
        assert new_user0.is_active

    # test functions
    # user_login, refresh_token, user_detail, user_logout
    # check jwt content
    def test_login(self):

        c = Client()

        # wrong user password
        response = c.post(LOGIN_URL, {'username': "user0", "password": "wrong_password"}, content_type="application/json")
        assert response.status_code == 403

        # correct user password
        response = c.post(LOGIN_URL, {'username': "user0", "password": PASSWORD}, content_type="application/json")
        assert response.status_code == 200

        jwt_token = response.cookies['jwt'].value.encode('utf-8')
        decoded = jwt.decode(jwt_token, self.public_key, algorithms=["RS256"])
        assert decoded['username'] == "user0"
        expires = decoded['expires']

        # refresh token
        sleep(1)
        response = c.post(REFRESH_TOKEN_URL)
        assert response.status_code == 200

        jwt_token = response.cookies['jwt'].value.encode('utf-8')
        decoded = jwt.decode(jwt_token, self.public_key, algorithms=["RS256"])
        assert decoded['username'] == "user0"
        new_expires = decoded['expires']

        assert (new_expires > expires)

        response = c.get(DETAIL_URL)
        assert response.status_code == 200
        assert response.json()['data']['username'] == "user0"
        assert list(response.json()['data'].keys()).count('mobile_phone') == 1

        response = c.get(PUBLIC_DETAIL_URL, {'username': 'user0'})
        assert response.status_code == 200
        assert response.json()['data']['username'] == "user0"
        assert list(response.json()['data'].keys()).count('mobile_phone') == 0

        response = c.get(LOGOUT_URL)
        assert response.status_code == 200
        response = c.get(DETAIL_URL)
        assert response.status_code == 401
        assert response.json()['err_code'] == -1
        assert response.json()['message'] == "Login Required"

        # user is not registered
        # 1. fudan email account is incorrect
        # TODO: might have some problems in the following tests.
        username = "13307130109"
        password = "wrong_password"
        nickname = "王耀辉"

        response = c.post(LOGIN_URL, {'username': username, "password": password}, content_type="application/json")
        assert response.status_code == 403
        assert response.json()['message'] == "用户不存在"

        # 2. fudan email account is correct
        password = "fake_password"  # [NOTE]: change this value to the real password of fudan email OR THE TEST WILL FAIL !!
        # TODO: the implementation of LOGIN_URL is changed, so the test following will fail.
        response = c.post(LOGIN_URL, {'username': username, "password": password}, content_type="application/json")
        assert response.json()['message'] == "Login success"
        assert response.status_code == 200
        account = Account.objects.get(user__username=username)
        assert account.user.is_active
        assert account.nickname == nickname

        jwt_token = response.cookies['jwt'].value.encode('utf-8')
        decoded = jwt.decode(jwt_token, self.public_key, algorithms=["RS256"])
        assert decoded['username'] == username

        # not existed user
        response = c.post(LOGIN_URL, {'username': "not_existed", "password": "password"}, content_type="application/json")
        assert response.status_code == 403
        assert response.json()['message'] == "用户不存在"

    # test functions
    # change_detail
    def test_change_detail(self):

        c = Client()
        response = c.post(LOGIN_URL, {'username': "user0", "password": PASSWORD}, content_type="application/json")
        assert response.status_code == 200

        new_detail = {
            "nickname": "nickname0",
            "gender": "M",
            "school": "计算机",
            "major": "计算机",
            "mobile_phone": "1231245124",
            "wechat": "12899109",
            "qq": "091288449",
        }

        response = c.post(CHANGE_DETAIL_URL, new_detail, content_type="application/json")
        assert response.status_code == 200

        account = Account.objects.get(user__username="user0")
        assert account.nickname == "nickname0"
        assert account.gender == "M"
        assert account.school == "计算机"
        assert account.major == "计算机"
        assert account.mobile_phone == "1231245124"
        assert account.wechat == "12899109"
        assert account.qq == "091288449"

    # test functions
    # change_password
    def test_change_password(self):
        c = Client()
        response = c.post(LOGIN_URL, {'username': 'user0', 'password': PASSWORD}, content_type="application/json")
        assert response.status_code == 200

        # wrong old password
        response = c.post(CHANGE_PASSWORD_URL, {"old_password": "wrong_password", "new_password": "new_password"}, content_type="application/json")
        assert response.status_code == 403

        # correct old password but unsafe new password
        unsafe_password = "password"
        response = c.post(CHANGE_PASSWORD_URL, {"old_password": PASSWORD, "new_password": unsafe_password}, content_type="application/json")
        assert response.status_code == 403
        assert(response.json()['message'] == "密码不安全，请设置6-20位包含大写字母，小写字母，数字和特殊字符中至少两种的密码")

        # correct old password
        response = c.post(CHANGE_PASSWORD_URL, {"old_password": PASSWORD, "new_password": "new_safe_password"}, content_type="application/json")
        assert response.status_code == 200

        # logout
        response = c.get(LOGOUT_URL)
        assert response.status_code == 200

        # login using old password
        response = c.post(LOGIN_URL, {"username": "user0", "password": "old_password"}, content_type="application/json")
        assert response.status_code == 403

        # login using new safe password
        response = c.post(LOGIN_URL, {"username": "user0", "password": "new_safe_password"}, content_type="application/json")
        assert response.status_code == 200

    # test functions
    # change_icon
    def test_change_icon(self):
        c = Client()
        response = c.post(LOGIN_URL, {'username': 'user0', 'password': PASSWORD}, content_type="application/json")
        assert response.status_code == 200

        with open("account/test_icon.png", "rb") as f:
            response = c.post(CHANGE_ICON_URL, {'picture': f})
            assert response.status_code == 200


class UtilsTestCase(TestCase):

    def test_password_safety_reg_exp(self):
        from account.utils import check_safe_password
        good_pwd_list = ['au2bf8eh', 'Password', '12345^&*']
        bad_pwd_list = ['geiuhvwuef', '3496239123', '!@&^$&^$%&@', 'AUHSIUHFWF', '1sd',
                        '3h9f82h3f8h2498gh394guh394hih23f92h83r9']
        for pwd in good_pwd_list:
            assert check_safe_password(pwd)
        for pwd in bad_pwd_list:
            assert not check_safe_password(pwd)