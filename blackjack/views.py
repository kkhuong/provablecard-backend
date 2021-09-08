from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
from django.core.exceptions import BadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .models import *


@api_view(['GET', 'POST'])
def hand_list(request):
    # GET list of hands, POST a new hand, DELETE all hands

    if request.method == 'GET':
        # gather all hands from database
        all_hands = {} # theoretically this is an object with a list of all hands, just for now
        return JsonResponse(all_hands)

    # create new hand
    if request.method == 'POST':
        request_data = JSONParser().parse(request)
        # validate
        # create new hand
        # return hand info
        hand_info = request_data # just for now
        return JsonResponse(hand_info, status=status.HTTP_201_CREATED) # or 200 response

    return JsonResponse({'detail': 'Invalid API request.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
def hand_detail(request, pk):
    try:
        # find hand by pk (id), possibly using # hand = Hand.objects.get(pk=pk)
        if request.method == 'PUT': # or POST
            # check if you can perform the action on the hand
            # if yes, do it
            # if no, return JsonResponse({'message': f'Cannot perform the {action} on hand id {pk}'}, status=status.HTTP_400_BAD_REQUEST)
            # now hand action is done
            pass
        hand_info = {'detail': pk} # just for now, we will gather the hand info (updated version), possibly by # hand = Hand.objects.get(pk=pk)
        return JsonResponse(hand_info)
    except:
        return JsonResponse({'detail': f'Cannot find hand with id {pk}'}, status=status.HTTP_404_NOT_FOUND)
