from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
from django.core.exceptions import BadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .models import Hand
import json


@api_view(['GET', 'POST'])
def hand_list(request):
    if request.method == 'GET':
        all_hands = Hand.objects.all()
        return JsonResponse({'results': list([h.to_json() for h in all_hands])})

    if request.method == 'POST':
        request_data = JSONParser().parse(request)
        # validate request_data
        hand = Hand(currency=request_data['currency'], wallet_address=request_data['address'], transaction_hash=request_data['txid'], initial_bet=float(request_data['bet']))
        hand.save()
        return JsonResponse(hand.to_json(), status=status.HTTP_201_CREATED) # or 200 response

    return JsonResponse({'detail': 'Invalid API request.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
def hand_detail(request, pk):
    try:
        if request.method == 'PUT': # or POST
            hand = Hand.objects.get(id=pk)
            request_data = JSONParser().parse(request)
            # validate request_data
            if hand.act(request_data['action'], additional_bet_amount=float(request_data['amount'])):
                hand.save()
            else:
                return JsonResponse({'message': f"Cannot perform the action {request_data['action']} on hand #{pk}"}, status=status.HTTP_400_BAD_REQUEST)
        hand = Hand.objects.get(id=pk)
        return JsonResponse(hand.to_json())
    except:
        return JsonResponse({'detail': f"Error finding hand with id {pk}"}, status=status.HTTP_404_NOT_FOUND)
