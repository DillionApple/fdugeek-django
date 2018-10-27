from django.http import JsonResponse

from utils.api_utils import get_json_dict

def login_required(func):

    def wrapper(request):
        if request.user.is_authenticated:
            return func(request)
        response = JsonResponse(get_json_dict(data={}, err_code=-1, message="Login Required"))
        response.status_code = 403
        return response
    
    return wrapper
