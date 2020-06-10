def effective_interest(r, m):
    """
    Author: Thomas Richmond
    Purpose: Convert a nominal interest into an effective interest.
    Parameters: r [float] - Nominal interest expressed as a decimal
                m [integer] - Compounding periods per year
    """
    return (1 + r / m) ** m - 1


def equivalent_interest(i, c, p):
    """
    Author: Thomas Richmond
    Purpose: Convert a periodically compounded interest rate to an
             equivalent interest for a certain payment period
    Parameters: i [float] - Interest being compounded at rate c,
                            expressed as a decimal
                c [integer] - Compounding periods per year
                p [integer] - Payment periods per year
    """
    return (1 + i) ** (c / p) - 1
