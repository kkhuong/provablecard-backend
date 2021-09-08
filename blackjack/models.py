from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

cards = ['As', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 'Ts', 'Js', 'Qs', 'Ks', 'Ad', '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', 'Td', 'Jd', 'Qd', 'Kd', 'Kc', 'Qc', 'Jc', 'Tc', '9c', '8c', '7c', '6c', '5c', '4c', '3c', '2c', 'Ac', 'Kh', 'Qh', 'Jh', 'Th', '9h', '8h', '7h', '6h', '5h', '4h', '3h', '2h', 'Ah']
pack = cards * 2

# Create your models here.
# class SubHand:
#     # fields are cards, status
#     cards = ArrayField(models.CharField(max_length=2), verbose_name='cards')
#     done = models.BooleanField(default=False)
#     bet = models.FloatField() # just for now

class Hand(models.Model):
    # fields are cards, subhands, currency, wallet_address
    currency = models.CharField(max_length=100)
    wallet_address = models.CharField(max_length=100)
    transaction_hash = models.CharField(max_length=100)
    initial_bet = models.FloatField()
    current_deck_position = models.IntegerField(default=0)
    current_hand_number = models.IntegerField(default=0)
    cards = ArrayField(models.CharField(max_length=2))
    subhands = models.JSONField(default={'hands': []})
    dealer_hand = ArrayField(models.CharField(max_length=2))
    date = models.DateTimeField(default=timezone.now)
