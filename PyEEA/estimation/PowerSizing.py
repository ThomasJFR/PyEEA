def psc(x, size_ratio, ref_cost):
    """
    Returns: Cost of a power-sizing model estimate as per the formula:
    
        tcost = ( size_ratio)^x * ref_cost

    """
    return ref_cost * size_ratio ** x


def pss(x, cost_ratio, ref_size):
    """
    Returns: Size of a power-sizing model estimate as per the formula:

        tsize = (cost_ratio)^-x * ref_size

    """
    return ref_size * (cost_ratio) ** -x
