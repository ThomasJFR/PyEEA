from math import inf, isinf
from typing import Iterable


def parse_d(d):
    """
    Author: Thomas Richmond
    Purpose: We expect an Annuity to occur over a finite duration.
             (for an infinite duration, refer to Perpetuity implementation)
             This duration does not necessarily have to start at the first period,
             so n is specified to be a list of two whole numbers, inclusively
             indicating the start and end period for the annuity. However, it may
             be desirable to assume n starts at one and supply a single integer value
             to specify the end date for syntactic clarity.
             This method is used to convert a nonspecific parameter n into a form
             compliant with the design of the library.
    Parameter: d [any] - An integer, whole-number float or 1 or 2-element list.
                         Integers, floats and one-element lists are assumed to specify
                         the end period of an annuity starting at period one.
    Returns: A two-element list of the start and end periods of the annuity.
    """

    if isinstance(d, Iterable):
        if len(d) > 2:
            return TypeError("Length of Iterable d must not exceed 2")
        if len(d) == 1:
            d = [0, d[0]]

        # Validate d0
        if int(d[0]) == d[0]:
            pass
        else:
            return TypeError("Type of d0 must be an integer!")

        # Validate d1
        if isinf(d[1]):
            pass
        elif int(d[1]) == d[1]:
            pass
        else:
            return TypeError("Type of d1 must be an integer or infinite!")

        if d[1] >= d[0]:
            pass
        else:
            return ValueError("Value of d0 must not exceed d1!")
        return d
    elif isinf(d):
        return parse_d([0, d])
    elif int(d) == d:
        return parse_d([0, d])
    else:
        raise TypeError("Type of d must be an integer or infinite, or list thereof")


def parse_ns(val):
    if type(val) == int:
        ns = (val,)  # Get the cashflows in a period as an array
    elif type(val) == tuple:
        ns = val  # Get the cashflows of multiple periods as a 2D array
    elif type(val) == slice:
        start = val.start or 0
        stop = val.stop + 1
        step = val.step or 1
        ns = range(start, stop, step)

    return ns


def get_final_period(cashflows, finite=True):
    from .cashflow import Present, Future, Annuity, Perpetuity, Dynamic
    from .taxation import Depreciation

    if not isinstance(cashflows, Iterable):
        cashflows = [cashflows]

    def final_period(cf):
        if isinstance(cf, Future):  # also accounts for present
            return cf.n
        elif isinstance(cf, Annuity):
            if finite and cf.d[1] is inf:
                return cf.d[0]
            else:
                return cf.d[1]
        elif isinstance(cf, Dynamic):
            return cf.d[1]
        elif isinstance(cf, Depreciation):
            return cf.d[1]
        else:
            return 0

    final_n = 0
    for cashflow in cashflows:
        n = final_period(cashflow)
        final_n = n if n > final_n else final_n
    return final_n
