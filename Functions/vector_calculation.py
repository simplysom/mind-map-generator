# Vector Calculation Functions --->

from .global_variables import *


def euclidean_distance(x, y):
    """
    Calculate Euclidean distance of power 2

    Keyword Arguments:
    x -- First vector of dimension n
    y -- Second vector of dimension n
    """
    return np.linalg.norm(x - y)


# Similarity between vectors
def cosine_similarity(x, y):
    """
    Calculates Cosine Similarity : cos = A.B / |A||B|
    Answer value ranges from -1(Perfectly Opposite) to 1(perfectly Similar).
    Value of 0 translates to no similarity.

    Keyword Arguments:
    x -- First Vector of dimension n
    y -- Second Vector of dimension n
    """
    x_val, y_val = x.copy(), y.copy()
    assert x_val.shape == y_val.shape
    mod_x = (x_val ** 2).sum() ** 0.5
    mod_y = (y_val ** 2).sum() ** 0.5
    cos = x.dot(y) / (mod_x * mod_y)
    assert cos is not np.nan
    return cos
