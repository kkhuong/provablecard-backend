from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from random import seed, randint
import copy
from decouple import config as envvar


def shuffle(seq, initial_seed=None):
    if initial_seed:
        seed(initial_seed)
    else:
        seed()
    shuffled_seq = copy.deepcopy(seq)
    for i in reversed(range(len(shuffled_seq))):
        j = randint(0, i)
        shuffled_seq[i], shuffled_seq[j] = shuffled_seq[j], shuffled_seq[i]
    return shuffled_seq

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
    transaction_hash = models.CharField(max_length=100, blank=False)  # 64 characters actually
    initial_bet = models.FloatField()
    current_deck_position = models.IntegerField(default=0)
    current_hand_number = models.IntegerField(default=0)
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

    def save(self, *args, **kwargs):
        if not self.subhands:  # first time setting up hand
            self.seed = str(int(str(envvar('SEED_PREFIX')), 16) + int(str(self.transaction_hash), 16))
            self.cards = shuffle(cards, int(self.seed))
            self.subhands = dict({'hands': []})
            self._initialize_main_hand()
            
            if self.dealer_hand[0][0] in 'TJQK':
                self._check_and_handle_dealer_bj()

        super().save(*args, **kwargs)

    def to_json(self):
        obj = {
            'id': self.id,
            'currency': str(self.currency),
            'address': str(self.wallet_address),
            'dealer_hand': self.dealer_hand,
            'subhands': self.subhands,
            'done': self.finished,
            'seed': int(self.seed), # remove this in production
            'deck': self.cards, # remove this in production
        }
        return obj
