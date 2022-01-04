import re
from .subject_object_extraction import *
from .logging import log, log_return
from . import global_variables as gv


@log
def pos_regex_matches(doc, pattern):
    """
    Extract sequences of consecutive tokens from a spacy-parsed doc whose
    part-of-speech tags match the specified regex pattern.

    Args:
        doc (``textacy.Doc`` or ``spacy.Doc`` or ``spacy.Span``)
        pattern (str): Pattern of consecutive POS tags whose corresponding words
            are to be extracted, inspired by the regex patterns used in NLTK's
            `nltk.chunk.regexp`. Tags are uppercase, from the universal tag set;
            delimited by < and >, which are basically converted to parentheses
            with spaces as needed to correctly extract matching word sequences;
            white space in the input doesn't matter.

            Examples (see ``constants.POS_REGEX_PATTERNS``):

            * noun phrase: r'<DET>? (<NOUN>+ <ADP|CONJ>)* <NOUN>+'
            * compound nouns: r'<NOUN>+'
            * verb phrase: r'<VERB>?<ADV>*<VERB>+'
            * prepositional phrase: r'<PREP> <DET>? (<NOUN>+<ADP>)* <NOUN>+'

    Yields:
        ``spacy.Span``: the next span of consecutive tokens from ``doc`` whose
        parts-of-speech match ``pattern``, in order of apperance
    """
    # standardize and transform the regular expression pattern...
    pattern = re.sub(r'\s', '', pattern)
    pattern = re.sub(r'<([A-Z]+)\|([A-Z]+)>', r'( (\1|\2))', pattern)
    pattern = re.sub(r'<([A-Z]+)>', r'( \1)', pattern)

    tags = ' ' + ' '.join(tok.pos_ for tok in doc)

    for m in re.finditer(pattern, tags):
        yield doc[tags[0:m.start()].count(' '):tags[0:m.end()].count(' ')]


# def get_relation(token1, token2):
#     output = [(token1, gv.DOC[i], token2) for i in range(token1.i, token2.i) if gv.DOC[i].pos_ == "VERB"]
#     if not output:
#         final_relation = (token1, '__X__', token2)
#     else:
#         rank = [gv.WORD_RANKING[x] for (token1, x, token2) in output if x in gv.WORD_RANKING.keys()]
#         if not rank:
#             rels = [x[1] for x in output]
#             rel2 = [x for x in rels if x.text not in ["is", "has", "have", "had", "was", "will"]]
#             final_relation = (token1, rels[int(len(rels) / 2)].text, token2)
#         else:
#             max_rank = max(rank)
#             final_relation = output[rank.index(max_rank)]
#     return final_relation

@log
@log_return
def get_relation(token1, token2):

    for SVO in gv.SVOs:
        lemma_lowered_svo = (SVO[0].lemma_.lower(), SVO[2].lemma_.lower())
        if token1.lemma_.lower() in lemma_lowered_svo and token2.lemma_.lower() in lemma_lowered_svo:
            print("SVO", lemma_lowered_svo, SVO[1])
            return (token1, SVO[1], token2)
            
    if gv.VERB_PHRASES is None:
        gv.VERB_PHRASES = list(pos_regex_matches(gv.DOC, r'<VERB>?<ADV>*<VERB>+'))
   
    verb_phrases = gv.VERB_PHRASES 
    
    fst, lst = (token1, token2) if token1.i < token2.i else (token2, token1)
    phr = [vp for vp in verb_phrases if vp.start > fst.i and vp.end < lst.i]
    if not phr:
        # print(token1,token2)
        return (token1, '__X__', token2)
    else:
        arr = []
        for vp in phr:
            simi = token1.similarity(vp) + token2.similarity(vp)
            arr.append((vp, simi))
        rel, _ = sorted(arr, key=lambda x: x[1])[-1]
        # print(arr)
        return (token1, rel.text, token2)
