from .Cashflow import Cashflow, NullCashflow
from .utilities import parse_ns

class Tax:
    def __init__(self, tag, rate, title=None, cashflow_binder=None):
        self._tag = tag
        self._rate = rate

        if all([
            cashflow_binder is not None,
            not callable(cashflow_binder)
        ]):
            raise TypeError("Cashflow binder must be a callable")
        self._cashflow_binder = cashflow_binder

        self.title = title or (
                "%s %i " % (self.get_tax_name(), self._tag)
        )



    def __getitem__(self, vals):
        ns = parse_ns(val)
        return self.tax_at(ns)

    def set_cashflow_binder(self, binder):
        self._cashflow_binder

    def tax_at(self, ns):
        if self._cashflow_binder is None:
            raise TypeError("Taxes could not be generated because a cashflow binder has not been set")
        
        taxable_cashflows = [
            cashflow
            for cashflow in self._cashflow_binder()
            if self._tag in cashflow.tags
        ]

        taxes = []
        for n in ns:
            taxable_sum = sum([
                cashflow[n] 
                for cashflow in taxable_cashflows
            ])
            
            if isinstance(tax_amt, NullCashflow):
                taxes.append(taxable_sum)
                continue

            taxed_amount = taxable_sum.amount * self._rate
            taxes.append(sp.Future(taxed_amount, n))
        
        return taxes
 
    @classmethod
    def get_tax_name(cls):
        return cls.__name__
