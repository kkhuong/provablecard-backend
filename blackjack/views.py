from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.exceptions import BadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import *

# Create your views here.
@csrf_exempt
def home(request):
    # if request.method == 'DELETE':
    #     raise BadRequest('')
    # body_unicode = request.body.decode('utf-8')
    # body = json.loads(body_unicode)
    # content = body['content']
    context = {
        'method': request.method,
        'debug': request.data,
        'posts': 'lst of posts',
        'title': 'Home',
    }
    return JsonResponse(context)
