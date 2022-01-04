from .global_variables import *
from .token_manipulation import make_unique
from collections import defaultdict


def info_dict_from_doc(DOC):
    import functools
    u_nodes = make_unique([t for t in DOC if t.pos_ is 'NOUN'])
    sum_freq = functools.reduce(lambda x, y:x+y, [t._.frequency for t in u_nodes])
    score = defaultdict(int)
    for t in u_nodes:
        score[t.lemma_.lower()] = t._.frequency / sum_freq
    return score


