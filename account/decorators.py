import jwt

from django.utils.timezone import datetime
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

from cs_plus import settings

from account.keys import PUBLIC_KEY

def login_required(func):

    def wrapper(request):

        try:
            jwt_token = request.COOKIES.get("jwt").encode('utf-8')
            decoded = jwt.decode(jwt_token, PUBLIC_KEY, algorithms=["RS256"])
            expire_date = datetime.strptime(decoded['expires'], "%Y-%m-%d %H:%M:%S")
            if (datetime.now() > expire_date):
                raise Exception("jwt expires")
            request.jwt_payload = decoded
            request.user = User.objects.get(username=decoded['username'])
        except:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        else:
            return func(request)
    
    return wrapper
