from ..cashflow import Cashflow, NullCashflow
from ..cashflow import Future, Dynamic

from ..utilities import parse_ns, parse_d

class Tax:
    def __init__(self, tag, rate, title=None):
        self._tag = tag
        self._rate = rate
        self._title = title or (
                "Tax on %s" % self._tag
        )

    def get_title(self):
        return self._title

    def generate_cashflow(self, project):
        def tax_fun(ns):
            ns = parse_ns(ns)
            
            taxable_cashflows = [
                    cashflow
                    for cashflow in project.get_cashflows()
                    if self._tag in cashflow.tags
            ] or [NullCashflow()]
            shielding_depreciations = [
                    depreciation
                    for depreciation in project.get_depreciations()
                    if self._tag in depreciation.tags
            ] or [NullCashflow()]

            taxes = []
            for n in ns:
                taxable_sum = sum([
                    cashflow[n] 
                    for cashflow in taxable_cashflows
                ])
                if isinstance(taxable_sum, NullCashflow):
                    taxes.append(taxable_sum)
                    continue

                shielding_sum = sum([
                    depreciation[n]
                    for depreciation in shielding_depreciations
                ])

                taxed_amount = (taxable_sum.amount + shielding_sum.amount) * self._rate
                taxes.append(Future(taxed_amount, n))
            
            return taxes
        return TaxCashflow(
            tax_fun, project._periods, 
            title=self.get_title(), shorthand="%s(%.2f%%)" % (self._tag, (self._rate * 100))
        )
 
class TaxCashflow(Dynamic):
    def __init__(self, tax_fun, d, title=None, shorthand=None):
        super().__init__(tax_fun, d, title)
        self._shorthand = shorthand

    def to_shorthand(self):
        return self._shorthand

    

