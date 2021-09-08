from random import seed, randint
import copy

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
