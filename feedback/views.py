import json

from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse, HttpResponse

from feedback.models import Feedback
from utils.api_utils import get_json_dict

# Create your views here.

@require_POST
def feedback(request):
    request.POST = json.loads(request.body.decode('utf-8'))
    
    # Each feedback should be no longer than 500 letters, or it will be truncated.
    feedback_info = request.POST.get('feedback')
    contact_email = request.POST.get('contact_email')
    if len(feedback_info) == 0:
        return JsonResponse(get_json_dict(data={}, err_code=-1, message="Empty Feedback"))
    else:
        feedback = Feedback(feedback=feedback_info, contact_email=contact_email)
        feedback.save()
        return JsonResponse(get_json_dict(data={}, err_code=0, message="Feedback Success"))
