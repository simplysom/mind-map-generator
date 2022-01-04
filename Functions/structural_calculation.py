# Structural Calculations -->

from .global_variables import *
from . import global_variables as gv
from .logging import log, log_return

# Structural Distance Functions
# Paragraph Distance
# Implementing Static Calculation through : e^(-4x)
# Later versions may include dynamic calculations of z-score by getting all pairs of p_distance to produce more subtle(smooth) values. : a = (x-mean)/ std; z-score = scipy.stats.norm.cdf(a)

# v1.3 New Distance Function ::

@log
def term_distance(term_a, term_b):
    """Calculates Term Distance using word sub-index by the formula : e^(x/r)
    r = word_range / sent_range
    """

    def min_dist_between_two_set(a, b):
        i, j = 0, 0
        min_diff = 100
        while i < len(a) and j < len(b):
            if min_diff > abs(a[i] - b[j]):
                x, y, min_diff = i, j, abs(a[i] - b[j])
            i, j = (i + 1, j) if a[i] < b[j] else (i, j + 1)
        return min_diff

    def in_sentence(a,b):
        a_sent_inst={na.sent for na in a._.instance_list}
        b_sent_inst={nb.sent for nb in b._.instance_list}
        common_sent=a_sent_inst.intersection(b_sent_inst)
        if common_sent:
            # print("\t\t", n1,n2)
            return True
    assert term_a._.instance_list is not []
    assert term_b._.instance_list is not []

    # if in_sentence(term_a,term_b):
    #     return 1

    ax = [x._.index.sid for x in term_a._.instance_list if not x._.index == None]
    bx = [x._.index.sid for x in term_b._.instance_list if not x._.index == None]
    min_dist = min_dist_between_two_set(ax, bx)
    value = np.e ** -(min_dist * 5 / gv.SENT_RANGE )
    return value

# Frequency Sum MD-TMP 1.1

@log
def freq_sum(a, b):
    """Get frequency Sum of the tokens a and b

    Keywords:
    a - 1st token object
    b - 2nd token object
    """
    summation = a._.frequency + b._.frequency
    return summation
