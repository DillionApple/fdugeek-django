import jwt
from time import sleep

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User

from account.models import *
from cs_plus import settings

LOGIN_URL = "/account/login/"
REGISTER_URL = "/account/register/"
CONFIRM_REGISTER_URL = "/account/confirm_register/"
LOGOUT_URL = "/account/logout/"
DETAIL_URL = "/account/detail/"
CHANGE_DETAIL_URL = "/account/change_detail/"
CHANGE_PASSWORD_URL = "/account/change_password/"
CHANGE_ICON_URL = "/account/change_icon/"
PUBLIC_KEY_URL = "/account/public_key/"
REFRESH_TOKEN_URL = "/account/refresh_token/"

class AccountTestCase(TestCase):

    public_key = None

    def setUp(self):
        c = Client()
        response = c.get(PUBLIC_KEY_URL)
        assert response.status_code == 200
        self.public_key = response.content

        user = User(username="user0")
        user.set_password("password")
        user.save()
        account = Account(user=user, nickname="nickname0")
        account.save()

    # test functions:
    # register, confirm_register
    def test_register(self):

        c = Client()

        # start to register a new user
        response = c.post(REGISTER_URL, {'username': 'new_user0', 'password': 'password'}, content_type="application/json")
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
        response = c.post(LOGIN_URL, {'username': "user0", "password": "password"}, content_type="application/json")
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

        response = c.get(LOGOUT_URL)
        assert response.status_code == 200
        response = c.get(DETAIL_URL)
        assert response.status_code == 401
        assert response.json()['err_code'] == -1
        assert response.json()['message'] == "Login Required"

    # test functions
    # change_detail
    def test_change_detail(self):

        c = Client()
        response = c.post(LOGIN_URL, {'username': "user0", "password": "password"}, content_type="application/json")
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
        response = c.post(LOGIN_URL, {'username': 'user0', 'password': 'password'}, content_type="application/json")
        assert response.status_code == 200

        new_password = "new_password"

        # wrong old password
        response = c.post(CHANGE_PASSWORD_URL, {"old_password": "wrong_password", "new_password": "new_password"}, content_type="application/json")
        assert response.status_code == 403

        # correct old password
        response = c.post(CHANGE_PASSWORD_URL, {"old_password": "password", "new_password": "new_password"}, content_type="application/json")
        assert response.status_code == 200

        # logout
        response = c.get(LOGOUT_URL)
        assert response.status_code == 200

        # login using old password
        response = c.post(LOGIN_URL, {"username": "user0", "password": "password"}, content_type="application/json")
        assert response.status_code == 403

        # login using
        response = c.post(LOGIN_URL, {"username": "user0", "password": "new_password"}, content_type="application/json")
        assert response.status_code == 200

    # test functions
    # change_icon
    def test_change_icon(self):
        c = Client()
        response = c.post(LOGIN_URL, {'username': 'user0', 'password': 'password'}, content_type="application/json")
        assert response.status_code == 200

        with open("account/test_icon.png", "rb") as f:
            response = c.post(CHANGE_ICON_URL, {'picture': f})
            assert response.status_code == 200