from ..cashflow import NullCashflow, Present, Future, Annuity, Perpetuity
from ..utilities import get_final_period
from math import isinf


def npw(cashflows, i, title=None) -> Present:
    """ Computes the Net Present Worth of a sequence of cashflows

    Converts each Cashflow in a sequence of cashflows to their Present
    equivalent using the to_pv() method for a given interest rate. The
    resultant sequence of Present cashflows is summed, yielding a single
    Present instance, which is the Net Present Worth. A title may be 
    optionally assigned to this value.

    For sequences of Cashflows including Dynamic instances alongside
    Perpetuity instances - for example, as might occur in a Project whose
    cashflows include a Tax object applied to a GeoPerpetuity - the Dynamic
    instance will attempt to compute the Perpetual Taxflow. Refer to Dynamic's
    implementation of to_pv() for additional details.
    
    Args:
        cashflows: A sequence of Cashflow instances
        i: An interest rate, expressed as a decimal
        title: Optional; The title to give the resultant Cashflow.

    Returns:
        Net Present Value as a Present instance

    See Also:
        Cashflow
        Present
        Dynamic
    """
    npw = sum([cf.to_pv(i) for cf in cashflows]) or NullCashflow()
    npw.set_title(title or "Net Present Worth")
    return npw


def nfw(cashflows, i, n, title=None) -> Future:
    """ Computes the Net Future Worth of a sequence of cashflows

    Converts each Cashflow in a sequence of cashflows to their Future
    equivalent using the to_fv() method for a given interest rate and period. 
    The resultant sequence of Future cashflows is summed, yielding a single 
    Future instance, which is the Net Present Worth. A title may be
    optionally assigned to this value.

    Args:
        cashflows: A sequence of Cashflow instances
        i: An interest rate, expressed as a decimal
        n: The period to which Cashflows are converted
        title: Optional; The title to give the resultant Cashflow.

    Returns:
        Net Future Value as a Future instance

    See Also:
        Cashflow
        Future
    """
    nfw = sum([cf.to_fv(i, n) for cf in cashflows]) or NullCashflow()
    npw.set_title(title or f"Net Future Worth")
    return nfw


def eacf(cashflows, i, d, title=None) -> Annuity:
    """ Computes the Equivalent Annual Cashflow of a sequence of cashflows

    Converts each Cashflow in a sequence of cashflows to their Annuity
    equivalent using the to_av() method for a given interest rate and duration. 
    The resultant sequence of Annuity cashflows is summed, yielding a single 
    Annuity instance, which is the Equivalent Annual Cashflow. A title may be
    optionally assigned to this value.

    Args:
        cashflows: A sequence of Cashflow instances
        i: An interest rate, expressed as a decimal
        d: The duration over which the resultant Annuity applies
        title: Optional; The title to give the resultant Cashflow

    Returns:
        Equivalent Annual Cashflow as an Annuity instance

    See Also:
        Cashflow
        Annuity
    """    
    eacf = sum([cf.to_av(i, d) for cf in cashflows]) or NullCashflow()
    eacf.set_title(title or "Equivalent Annual Cashflow")
    return eacf


def epcf(cashflows, i, d0, title=None) -> Perpetuity:
    """ Computes the Net Present Worth of a sequence of cashflows

    Converts each Cashflow in a sequence of cashflows to their Future
    equivalent using the to_fv() method for a given interest rate and period. 
    The resultant sequence of Future cashflows is summed. This is then
    converted to a Perpetuity, which is the Perpetual Annual Cashflow, by
    multiplying the amount by the interest rate. A title may be optionally
    assigned to this value.

    Args:
        cashflows: A sequence of Cashflow instances
        i: An interest rate, expressed as a decimal
        d0: The start period for the Perpetuity
        title: Optional; The title to give the resultant Cashflow

    Returns:
        Equivalent Annual Cashflow as an Annuity instance

    See Also:
        Cashflow
        Future
        Perpetuity
    """ 
    fv = sum([cf.to_fv(i, d0) for cf in cashflows])
    epcf = Perpetuity(fv.amount * i, d0)
    epcf.set_title(title or "Equivalent Perpetual Cashflow")
    return epcf


def bcr(cashflows, i=0) -> float:
    """ Computes a Benefit-To-Cost ratio for a sequence of cashflows

    Sums the positive and negative amount of each Cashflow in a sequence of
    cashflows, then return the absolute quotient of the two as a ratio
    of benefits to costs.

    The interest is NOT considered, so this valuation does not consider time.

    Args:
        cashflows: A sequence of Cashflow instances
        i: Optional; Currently does nothing

    Returns:
        None if there are no benefits or no costs, as this means there is no BCR.
        Else, returns a floating point value. If greater than unity, a greater 
            absolute amount of cash is flowing into the project than out; if 
            less than unity, the vice versa is true. At unity, cash inflow and
            outflow is equal in magnitude.
    """
    pvs = [cf.to_pv(0) for cf in cashflows]
    rvnus = sum([pv for pv in pvs if pv > 0])
    costs = sum([pv for pv in pvs if pv < 0])
    if all([rvnus, costs]):
        return -(rvnus.amount / costs.amount)
    else:
        return None

def irr(cashflows, i0=0.1) -> float:
    """ Computes the Internal Rate of Return for a sequence of Cashflows
    
    Computes the interest rate for which the net present value of the Cashflow
    sequence is zero. This is done using the Powell Hybrid Method and
    implemented using scipy's fsolve method.

    For projects containing complex sequences of Cashflows, IRR computations
    can become unstable, or there may be several IRRs. For such cases, it is
    generally advisable to use an alternate valuation technique, such as
    the modified internal rate of return. (MIRR)

    Args:
        cashflows: A sequence of Cashflow instances
        i0: An initial guess for the solver

    Returns:
        The internal rate of return expressed as a decimal, or None if it
            could not be computed.
    """
    # IRR only exists if we have both net positive AND net negative cashflows
    # over all periods.
    nf = get_final_period(cashflows, finite=True)
    # Note that we need to check longer than the final finite period to account
    # for cashflows incurred via perpetuities.
    net_cashflows = [sum([cf[n] for cf in cashflows]) for n in range(nf + 2)]
    if not all([
            any([ncf > 0 for ncf in net_cashflows]),
            any([ncf < 0 for ncf in net_cashflows]),
    ]):
        return None

    # Compute IRR by solving where NPW is zero
    from scipy.optimize import fsolve
    def irr_fun(i):
        return npw(cashflows, i[0]).amount
    irrs, _, success, _ = fsolve(irr_fun, i0, factor=0.1, full_output=True)

    return irrs[0] if success else None


def mirr(cashflows, e_inv, e_fin) -> float:
    """ Computes the Modified IRR for a sequence of cashflows

    Computes the interest rate for which the Net Present Worth of a sequence 
    of cashflows whose net negative and net positive cashflows per period are
    cast to the Present or final-period Future, respectively, is zero. Two
    unique interest rates - called finance and investment rates - are used to
    cast the negative and positive cashflows, respectively.

    Computing the MIRR is much easier than computing the IRR and is more
    easily applied to projects with complex cashflows. 
    
    Args:
        e_inv: Investment rate, expressed as a decimal
        e_fin: Finance rate, expressed as a decimal

    Returns:
        The Modified Internal Rate of Return, expressed as a decimal
    """
    nf = get_final_period(cashflows)
    if isinf(nf):
        return None
   
    net_cashflows = [sum([cf[n] for cf in cashflows]) for n in range(nf + 1)]
    if not all(
        [
            any([ncf > 0 for ncf in net_cashflows]),
            any([ncf < 0 for ncf in net_cashflows]),
        ]
    ):
        return None

    fv_rvnu = sum([ncf.to_fv(e_fin, nf) for ncf in net_cashflows if ncf > 0]) or NullCashflow()
    pv_cost = sum([ncf.to_pv(e_inv) for ncf in net_cashflows if ncf < 0])

    mirr = (fv_rvnu.amount / -pv_cost.amount)**(1/nf) - 1
    return mirr

