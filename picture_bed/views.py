import time

from django.views.decorators.http import require_POST
from django.http import JsonResponse

from account.decorators import login_required
from utils.api_utils import get_json_dict
from utils.util_functions import get_md5
from picture_bed.models import Picture

@require_POST
@login_required
def upload_picture(request):
    """
    post form:
      picture: <image_file>
    response:
      {
        "err_code": 0,
        "message": "Success",
        "data": {
          "picture_url": "/statics/images/<username>/<time>_<md5>"
        }
      }
    """
    picture = request.FILES['picture']
    picture.name = "{timestamp}_{picture_name}".format(
        timestamp = int(round(time.time() * 1000)),
        picture_name = get_md5(picture.read())
    )

    picture_obj = Picture(picture=picture, user=request.user)
    picture_obj.save()

    json_dict = get_json_dict(data={})
    json_dict['data']['picture_url'] = picture_obj.picture.url
    return JsonResponse(json_dict)
