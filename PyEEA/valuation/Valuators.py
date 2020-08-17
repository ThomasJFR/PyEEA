from ..cashflow import NullCashflow, Present, Future, Annuity, Perpetuity
from ..utilities import get_final_period
from math import isinf


def npw(cashflows, i, title=None) -> Present:
    npw = sum([cf.to_pv(i) for cf in cashflows]) or NullCashflow()
    npw.set_title(title or "Net Present Worth")
    return npw


def nfw(cashflows, i, n, title=None) -> Future:
    nfw = sum([cf.to_fv(i, n) for cf in cashflows]) or NullCashflow()
    npw.set_title(title or f"Net Future Worth")
    return nfw


def eacf(cashflows, i, d, title=None) -> Annuity:
    eacf = sum([cf.to_av(i, d) for cf in cashflows]) or NullCashflow()
    eacf.set_title(title or "Equivalent Annual Cashflow")
    return eacf


def epcf(cashflows, i, d0, title=None) -> Perpetuity:
    pv = sum([cf.to_pv(i) for cf in cashflows])
    epcf = Perpetuity(pv.amount * i, d0)
    epcf.set_title(title or "Equivalent Perpetual Cashflow")
    return epcf


def bcr(cashflows, i=0) -> float:
    pvs = [cf.to_pv(0) for cf in cashflows]
    rvnus = sum([pv for pv in pvs if pv > 0])
    costs = sum([pv for pv in pvs if pv < 0])
    if all([rvnus, costs]):
        return -(rvnus.amount / costs.amount)
    else:
        return None


def irr(cashflows, i0=0.1) -> float:
    # IRR only exists if we have both net positive AND net negative cashflows over all periods.
    # Note that we need to check longer than the final period in case of perpetuities.
    nf = get_final_period(cashflows, finite=True)
    net_cashflows = [sum([cf[n] for cf in cashflows]) for n in range(nf + 2)]

    if not all(
        [
            any([ncf > 0 for ncf in net_cashflows]),
            any([ncf < 0 for ncf in net_cashflows]),
        ]
    ):
        return None

    # Compute IRR by solving where npw is zero
    from scipy.optimize import fsolve

    def irr_fun(i):
        return npw(cashflows, i[0]).amount

    irrs, _, success, _ = fsolve(irr_fun, i0, factor=0.1, full_output=True)

    return irrs[0] if success else None


def mirr(cashflows, e_inv, e_fin, i0=0.1) -> float:
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
