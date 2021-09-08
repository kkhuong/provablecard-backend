import copy
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from decouple import config as envvar
from .utils import shuffle


DEFAULT_DECK = ['As', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 'Ts', 'Js', 'Qs', 'Ks', 'Ad', '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', 'Td', 'Jd', 'Qd', 'Kd', 'Kc', 'Qc', 'Jc', 'Tc', '9c', '8c', '7c', '6c', '5c', '4c', '3c', '2c', 'Ac', 'Kh', 'Qh', 'Jh', 'Th', '9h', '8h', '7h', '6h', '5h', '4h', '3h', '2h', 'Ah']


class Hand(models.Model):
    currency = models.CharField(max_length=100)
    wallet_address = models.CharField(max_length=100)
    transaction_hash = models.CharField(max_length=100, blank=False)  # 64 characters actually
    initial_bet = models.FloatField()
    current_hand_number = models.IntegerField(default=0)
    amount_won = models.FloatField(default=0.0)
    seed = models.TextField(blank=False)
    cards = ArrayField(models.CharField(max_length=2))
    subhands = models.JSONField()
    dealer_hand = ArrayField(models.CharField(max_length=2))
    finished = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def _draw(self):
        return self.cards.pop()

    def _hit_player_hand(self, hand_number):
        self.subhands['hands'][hand_number]['cards'].append(self._draw())

    def _create_subhand(self, bet=0.0, card=None):  # bet = 0.0 for now
        hand = dict({'cards': ([card] if card else []), 'done': False, 'bet': bet})
        self.subhands['hands'].insert(self.current_hand_number + 1, hand)

    def _initialize_subhand(self, hand_number):
        cards_to_draw = 2 - len(self.subhands['hands'][hand_number]['cards'])
        for _ in range(cards_to_draw):
            self._hit_player_hand(hand_number)

    def _initialize_main_hand(self):
        self._create_subhand(bet=self.initial_bet)
        self._initialize_subhand(self.current_hand_number)
        self.dealer_hand = [self._draw()]

    def _check_and_handle_dealer_bj(self):
        # dealer shows 10, no insurance possible
        if self.dealer_hand[0][0] in 'TJQK' and self.cards[0][0] == 'A':
            self.finished = True
            self.dealer_hand.append(self.cards[0])
            self.subhands['hands'][self.current_hand_number]['done'] = True

        # dealer shows Ace, offer insurance.... BUT NO INSURANCE FOR NOW
        elif (self.dealer_hand[0][0] == 'A' and self.cards[0][0] in 'TJQK'):
            # just do the same thing for now
            self.finished = True
            self.dealer_hand.append(self.cards[0])
            self.subhands['hands'][self.current_hand_number]['done'] = True

    def act(self, action):
        # for now, see if action is a valid character
        return len(action) == 1 and action in 'ynhsdp'
        # eventually, perform the action and return True on success. 

    def save(self, *args, **kwargs):
        if not self.subhands:  # first time setting up hand
            self.seed = str(int(str(envvar('SEED_PREFIX')), 16) + int(str(self.transaction_hash), 16))
            self.cards = shuffle(DEFAULT_DECK, int(self.seed))
            self.subhands = dict({'hands': []})
            self._initialize_main_hand()
            
            # dealer bj no insurance possible
            if self.dealer_hand[0][0] in 'TJQK':
                self._check_and_handle_dealer_bj()

        if self.finished:
            # handle payouts
            pass

        super().save(*args, **kwargs)

    def to_json(self):
        obj = {
            'id': self.id,
            'currency': str(self.currency),
            'address': str(self.wallet_address),
            'dealer_hand': self.dealer_hand,
            'subhands': self.subhands,
            'done': self.finished,
            'amount_won': float(self.amount_won),
            'seed': int(self.seed), # remove this in production
            'deck': self.cards, # remove this in production
        }
        return obj
