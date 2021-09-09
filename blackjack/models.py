import copy
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from decouple import config as envvar
from .utils import shuffle, can_split


DEFAULT_DECK = ['As', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 'Ts', 'Js', 'Qs', 'Ks', 'Ad', '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', 'Td', 'Jd', 'Qd', 'Kd', 'Kc', 'Qc', 'Jc', 'Tc', '9c', '8c', '7c', '6c', '5c', '4c', '3c', '2c', 'Ac', 'Kh', 'Qh', 'Jh', 'Th', '9h', '8h', '7h', '6h', '5h', '4h', '3h', '2h', 'Ah']
INSURANCE_YES = 'y'
INSURANCE_NO = 'n'
SURRENDER = 'l'
SPLIT = 'p'
DOUBLE = 'd'
HIT = 'h'
STAND = 's'

BJ_HARD = 'hard'
BJ_SOFT = 'soft'

def rank_to_value(card):
    r = card[0]
    rnks = '_A23456789TJQK'
    return min(10, rnks.index(r))

def value(hand):
    if len(hand) < 2:
        raise ValueError

    # calculate value
    total = [0]
    contains_ace = False
    for card in hand:
        if card[0] != 'A':
            total = [i + rank_to_value(card) for i in total]
        else:
            contains_ace = True
            soft_totals = [i+1  for i in total]
            hard_totals = [i+11 for i in total]
            total = soft_totals + hard_totals

    # value
    val = min(total) if (min(total) > 21) else max(filter(lambda x: x<=21,total))
    # hard or soft
    if len(list(filter(lambda x: x<=11,total))) != 0 and contains_ace: hs = BJ_SOFT
    else: hs = BJ_HARD

    return (val, hs)

def total(hand):
    val, _ = value(hand)
    return val

def is_busted(hand):
    if len(hand) < 2: return False
    val, _ = value(hand)
    return val > 21

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
    action_history = ArrayField(models.CharField(max_length=1), default=list)
    finished = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def _draw(self):
        return self.cards.pop()

    def _hit_player_hand(self, hand_number):
        card = self._draw()
        self.subhands['hands'][hand_number]['cards'].append(card)
        return card

    def _create_subhand(self, bet=0.0, card=None):  # bet = 0.0 for now
        hand = dict({'cards': ([card] if card else []), 'done': False, 'bet': bet, 'paid': False})
        self.subhands['hands'].insert(self.current_hand_number + 1, hand)

    def _initialize_subhand(self, hand_number):
        cards_to_draw = 2 - len(self.subhands['hands'][hand_number]['cards'])
        for _ in range(cards_to_draw):
            self._hit_player_hand(hand_number)

    def _initialize_main_hand(self):
        self._create_subhand(bet=self.initial_bet)
        self._initialize_subhand(self.current_hand_number)
        self.dealer_hand = [self._draw()]

    def _check_dealer_bj(self):
        if self.dealer_hand[0][0] in 'TJQK' and self.cards[0][0] == 'A':
            return True
        if (self.dealer_hand[0][0] == 'A' and self.cards[0][0] in 'TJQK'):
            return True
        return False

    def _check_and_handle_dealer_bj(self):
        if self._check_dealer_bj():
            self.finished = True
            self.dealer_hand.append(self.cards[0])
            self.subhands['hands'][self.current_hand_number]['done'] = True
            self.current_hand_number += 1
            return True
        return False

    def _evaluate_player_hand(self, hand_number):
        score = value(self.subhands['hands'][hand_number]['cards'])
        print("ABLE TO COMPUTE HAND")
        if score > 21:
            self.subhands['hands'][hand_number]['score'] = -1
            return (-1, False)

        self.subhands['hands'][hand_number]['score'] = score
        print("ABLE TO SET SCORE")
        return (score, True)


    def _get_action_set(self):
        ans = []
        if self.finished:
            return ans
        if self.dealer_hand[0][0] == 'A' and len(self.action_history) == 0:
            ans.append(INSURANCE_YES)
            ans.append(INSURANCE_NO)
            return ans

        hand = self.subhands['hands'][self.current_hand_number]
        if len(self.subhands['hands']) == 1 and len(hand['cards']) == 2 and not hand['done']:
            ans.append(SURRENDER)

        # can split
        if can_split(self.subhands['hands'][self.current_hand_number]['cards']) and not hand['done']:
            ans.append(SPLIT)

        # can double
        if (not hand['done']) and len(hand['cards']) == 2:
            ans.append(DOUBLE)

        # can hit can stand
        if not hand['done']:
            ans.append(HIT)
            ans.append(STAND)

        return ans

    def act(self, action, additional_bet_amount=0.0):
        print("GOT INTO ACT FUNCTION")
        if not (len(action) == 1 and action in self._get_action_set()):
            return False

        print("ACT FUNCTION DECIDED THAT ACTION IS VALID")
        if action == INSURANCE_NO:
            self._check_and_handle_dealer_bj()
        elif action == INSURANCE_YES:
            # check if payment for additional_bet_amount has been received
            print("WANT TO BUY INSURANCE")
            if self._check_and_handle_dealer_bj():
                self.amount_won += 2*additional_bet_amount
        elif action == SURRENDER:
            print("GOT INTO SURRENDER")
            self.amount_won += 0.5 * self.subhands['hands'][self.current_hand_number]['bet']
            self.subhands['hands'][self.current_hand_number]['paid'] = True
            self.subhands['hands'][self.current_hand_number]['done'] = True
            self.current_hand_number += 1
        elif action == SPLIT:
            # check if payment for additional_bet_amount has been received
            raise NotImplemented
        elif action == DOUBLE:
            # check if payment for additional_bet_amount has been received
            self._hit_player_hand(self.current_hand_number)
            self.subhands['hands'][self.current_hand_number]['bet'] += additional_bet_amount
            self.subhands['hands'][self.current_hand_number]['done'] = True
            self.current_hand_number += 1
        elif action == HIT:
            self._hit_player_hand(self.current_hand_number)
            if is_busted(self.subhands['hands'][self.current_hand_number]['cards']):
                self.subhands['hands'][self.current_hand_number]['done'] = True
                self.current_hand_number += 1
        elif action == STAND:
            print("GOT INTO STAND LOGIC")
            self.subhands['hands'][self.current_hand_number]['done'] = True
            self.current_hand_number += 1

        # no more action
        print("CURRENT HAND NUMBER", self.current_hand_number)
        if self.current_hand_number >= len(self.subhands['hands']):
            print("GOT HERE 9472")
            self.finished = True

        self.action_history.append(action)
        print("GOT HERE2")
        return True

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
            # reveal holecard
            if len(self.dealer_hand) == 1:
                self.dealer_hand.append(self.cards[0])

            is_natural = lambda : False # for now
            # handle naturals
            if self._check_dealer_bj() and not is_natural():
                # player lost, hand is over. DONE
                pass # DONE
            elif is_natural() and not self._check_dealer_bj():
                # pay out 1.5*self.initial_bet
                pass
            elif is_natural() and self._check_dealer_bj():
                # pay out self.amount_won + 1.5*self.initial_bet
                pass
            else:
                # if got here, then just go ahead and play out dealer hand... and then pay out accordingly
                print("USUAL HAND NO BJ FOR BOTH")

                need_to_have_dealer_play_her_hand = False
                for i in range(len(self.subhands['hands'])):
                    _, logic = self._evaluate_player_hand(i)
                    need_to_have_dealer_play_her_hand = need_to_have_dealer_play_her_hand or logic

                # see if dealer needs to act
                if need_to_have_dealer_play_her_hand:
                    # play out dealer
                    # go thru all subhands, if paid, skip. else, compare score and pay if strictly higher
                    pass
                else:
                    # all busted hands, return doing nothing
                    pass # DONE

        print("BEFORE SAVING OBJECT")
        super().save(*args, **kwargs)
        print("AFTER SAVING OBJECT")

    def to_json(self):
        obj = {
            'id': self.id,
            'currency': str(self.currency),
            'address': str(self.wallet_address),
            'dealer_hand': self.dealer_hand,
            'subhands': self.subhands,
            'action_set': self._get_action_set(),
            'history': "".join(self.action_history),
            'done': self.finished,
            'amount_won': float(self.amount_won),
            'seed': int(self.seed), # remove this in production
            'deck': self.cards, # remove this in production
        }
        return obj
