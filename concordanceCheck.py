from config import ConcordanceSignal
from scipy.stats import spearmanr, kendalltau


# this function checks if the two ranks passed as arguments are 'stable' or not, returning a ConcordanceSignal, and also a value of the correlation
# The concurdance is defined according the value returned by the correlation function that is passed as an argument
# Options for the correlation function are: spearman, kendall's tau and custom

from typing import List, Tuple, Callable
def concordanceCheck(rank1: List[float], rank2: List[float], correlation_func: Callable[[List[float], List[float]], Tuple[float, float]] = kendalltau) -> Tuple[ConcordanceSignal, float]:
    """
    Checks if the two ranks passed as arguments are 'stable' or not, returning a ConcordanceSignal and a value of the correlation.
    
    Parameters:
    rank1 (list): The first rank list.
    rank2 (list): The second rank list.
    correlation_func (function): The correlation function to use (e.g., spearman, kendall's tau, custom).
    
    Returns:
    tuple: A tuple containing a ConcordanceSignal and the correlation value.
    """
    correlation = correlation_func(rank1, rank2)[0]
    if correlation == 1:
        return ConcordanceSignal.PERFECT, correlation
    elif correlation > .9:
        return ConcordanceSignal.VERYSTRONG, correlation
    elif correlation > .7:
        return ConcordanceSignal.STRONG, correlation
    elif correlation > .4:
        return ConcordanceSignal.MODERATE, correlation
    elif correlation > .1:
        return ConcordanceSignal.WEAK, correlation
    elif correlation > 0:
        return ConcordanceSignal.NEGLIGIBLE, correlation
    else:
        return ConcordanceSignal.NEGATIVE, correlation



