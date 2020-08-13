from ..cashflow import NullCashflow, Present, Future, Annuity, Perpetuity
from ..utilities import parse_d, get_last_period
from typing import Union

def npw(cashflows, i, title=None) -> Present:
    npw = sum([cf.to_pv(i) for cf in cashflows]) or NullCashflow()
    npw.set_title(title or "Net Present Worth")
    return npw

def nfw(cashflows, i, n, title=None) -> Future:
    nfw = sum([cf.to_fv(i, n) for cf in cashflows]) or NullCashflow()
    npw.set_title(title or f"Net Future Worth")
    return nfw

def eacf(cashflows, i, d, title=None) -> Annuity:
    d = parse_d(d)
    eacf = sum([cf.to_av(i, d) for cf in cashflows]) or NullCashflow()
    eacf.set_title(title or "Equivalent Annual Cashflow")
    return eacf

def epcf(cashflows, i, d0, title=None) -> Perpetuity:
    pv = sum([cf.to_pv(i).amount for cf in cashflows])
    epcf = Perpetuity(pv.amount * i, d0)
    epcf.set_title(title or "Equivalent Perpetual Cashflow")
    return epcf

def bcr(cashflows) -> float:
    nf = get_last_period(cashflows)
    net_cashflows = [sum([cf[n] for cf in cashflows]) for n in range(nf+1)]
    rvnus = sum([ncf.to_pv(0) for ncf in net_cashflows if ncf > 0])
    costs = sum([ncf.to_pv(0) for ncf in net_cashflows if ncf < 0])
    if all([rvnus, costs]):
        return -(rvnus.amount / costs.amount)
    else:
        return None

def irr(cashflows, i0=0) -> float:
    from scipy.optimize import fsolve
    
    # IRR only exists if BCR exists
    if not bcr(cashflows):
        return None

    def irr_fun(i):
        return npw(cashflows, i[0]).amount
    irrs, _, success, _ = fsolve(irr_fun, i0, factor=0.1, full_output=True)
    
    if success:
        return irrs[0]
    else:
        return None

def mirr(cashflows, e_inv, e_fin, i0=0) -> float:
    nf = get_last_period(cashflows)
    net_cashflows = [sum([cf[n] for cf in cashflows]) for n in range(nf+1)]
    fv_rvnu = sum([ncf.to_fv(e_fin, nf) for ncf in net_cashflows if ncf > 0])
    pv_cost = sum([ncf.to_pv(e_inv)     for ncf in net_cashflows if ncf < 0])
    return irr([pv_cost, fv_rvnu], i0)
