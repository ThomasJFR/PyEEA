def psc(x, rsize, rcost, tsize):
    """
    Returns: Cost of a power-sizing model estimate as per the formula:
    
                  tsize
        tcost = ( ----- )^x * rcost
                  rsize
    """
    return rcost * (tsize / rsize) ** x

def pss(x, rcost, rsize, tcost):
    """
    Returns: Size of a power-sizing model estimate as per the formula:
    
                  tcost
        tsize = ( ----- )^-x * rsize
                  rcost
    """
    return rsize * (tcost / rcost) ** -x
