from ..cashflow import Cashflow, NullCashflow
from ..cashflow import Future, Perpetuity, Dynamic

from ..utilities import parse_ns, parse_d, get_final_period

class Tax:
    def __init__(self, tag, rate, title=None):
        self._tag = tag
        self._rate = rate
        self._title = title or (
                "Tax on %s" % self._tag
        )

    def get_title(self):
        return self._title

    def generate_cashflow(self, cashflows=[], depreciations=[]):
        def tax_fun(_, n): 
            taxable_cashflows = [
                    cashflow
                    for cashflow in cashflows
                    if self._tag in cashflow.tags
            ] or [NullCashflow()]
            shielding_depreciations = [
                    depreciation
                    for depreciation in depreciations
                    if self._tag in depreciation.tags
            ] or [NullCashflow()]

            taxable_sum = sum([
                cashflow[n] 
                for cashflow in taxable_cashflows
            ])
            shielding_sum = sum([
                depreciation[n]
                for depreciation in shielding_depreciations
            ])

            taxed_amount = (taxable_sum - shielding_sum) * self._rate
            return taxed_amount

        return TaxCashflow(
            tax_fun, get_final_period(cashflows, finite=True), 
            title=self.get_title(), shorthand="%s(%.2f%%)" % (self._tag, (self._rate * 100))
        )
 
class TaxCashflow(Dynamic):
    def __init__(self, tax_fun, d, title=None, shorthand=None):
        super().__init__(tax_fun, d, title)
        self._shorthand = shorthand

    def to_shorthand(self):
        return self._shorthand

    def to_pv(self, i):
        pv = super().to_pv(i)
        
        # Account for Perpetuities
        if type(ptax := self._amount_fun(self, self.d[1] + 1)) is not NullCashflow:
            pv += Perpetuity(ptax.amount, self.d[1] + 1).to_pv(i)

        return pv
        
