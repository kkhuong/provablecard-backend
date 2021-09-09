from random import seed, randint
import copy

def float_equal(a, b, tol=1e-9):
    return abs(a-b) <= tol

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

# here hand is a list of cards
def can_split(hand):
    if len(hand) != 2:
        return False
    if hand[0][0] == hand[1][0]:
        return True
    return hand[0][0] in 'TJQK' and hand[1][0] in 'TJQK'
