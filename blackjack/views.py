from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
from django.core.exceptions import BadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .models import Hand


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
        hand = Hand(currency='BTC', wallet_address='3FZbgi29cpjq2GjdwV8eyHuJJnkLtktZc5', transaction_hash='c1596721ece27da5cdfb60018829f29415b206468d4d382f34c7882c75e4772e', initial_bet=0.00001, cards=['As', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 'Ts', 'Js', 'Qs', 'Ks', 'Ad', '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', 'Td', 'Jd', 'Qd', 'Kd', 'Kc', 'Qc', 'Jc', 'Tc', '9c', '8c', '7c', '6c', '5c', '4c', '3c', '2c', 'Ac', 'Kh', 'Qh', 'Jh', 'Th', '9h', '8h', '7h', '6h', '5h', '4h', '3h', '2h', 'Ah'])
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
