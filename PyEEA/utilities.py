
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
    isint = lambda x: any([type(x) is int, type(x) is float and x // 1 == x])

    if type(d) is list:
        if len(d) == 1 and isint(d[0]):
            return [0, int(d[0])]
        elif len(d) == 2 and isint(d[0]) and isint(d[1]):
            return [int(d[0]), int(d[1])]
        else:
            raise ValueError(
                "Argument n in list form must contain whole numbers,"
                + "and its length must not exceed 2"
            )
    elif isint(d):
        return [0, int(d)]
    else:
        raise TypeError(
            "Type of argument n <%s> is not supported;" % type(d)
            + "must be whole number or list of whole numbers"
        )


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

def get_last_period(cashflows, ignore_perpetuities=True):
    from .cashflow import Present, Future, Annuity, Perpetuity, Dynamic
    from .taxation import Depreciation
    def final_period(cf):
        if isinstance(cf, Future):  # also accounts for present
            return cf.n
        elif isinstance(cf, Annuity):
            return cf.d[1]
        elif isinstance(cf, Perpetuity):
            return 0 if ignore_perpetuities else float('inf')
        elif isinstance(cf, Dynamic):
            return cf.d[1]
        elif isinstance(cf, Depreciation):
            return cf.d[1]
        else:
            return 0
    max_n = 0
    for cashflow in cashflows:
        n = final_period(cashflow)
        max_n = n if n > max_n else max_n
    return max_n
