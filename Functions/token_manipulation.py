# Token Manipulation Functions --->
from collections import defaultdict, OrderedDict
import spacy
from . import global_variables as gv
from .logging import log, log_return

# Indexing of Tokens to a private system.


def set_index():
    """No-param function. Sets index <custom variable> for each token.
    Uses named tuple "Index" of the format(pid, sid, wid)
    Each successive paragraph, sentence, word recieves an incrementing ID

    Returns: None

    Note:
    Sets Global Variable <SENT_RANGE, WORD_RANGE, DOC>
    """
    gv.SENT_RANGE = len(list(gv.DOC.sents))
    gv.WORD_RANGE = len(list(gv.DOC))
    spacy.tokens.Token.set_extension('index', default=None, force=True)
    pc, sc, wc = 0, 0, 0
    for t in gv.DOC:
        if t.text is '\n':
            pc += 1
        if t.is_sent_start:
            sc += 1
        if not t.is_punct and t.text is not '\n':
            t._.index = gv.Index(pc, sc, wc)
            wc += 1


#  Frequency Counts and Instance List and unique tokens
def set_extentions(doc):
    """No-param function. Sets 'frequency' and 'instance_list' variable for each token.
    The frequency is calculated by lemma_.lower() word of the noun phrase.
    And lemma_.lower() is used to add instance to instance list.

    Returns: None
    """

    freq_count = defaultdict(int)
    instance_list = defaultdict(list)
    for t in doc:
        freq_count[t.lemma_.lower()] += 1
        instance_list[t.lemma_.lower()].append((t))

    def get_freq(t): return freq_count[t.lemma_.lower()]

    def get_instance_list(t): return instance_list[t.lemma_.lower()]

    spacy.tokens.Token.set_extension('frequency', getter=get_freq, force=True)
    spacy.tokens.Token.set_extension('instance_list', getter=get_instance_list, force=True)
    return doc


@log
def make_unique(tokens):
    uniq = OrderedDict()
    for t in tokens:
        uniq.setdefault(t.lemma_.lower(), t)
    return list(uniq.values())
