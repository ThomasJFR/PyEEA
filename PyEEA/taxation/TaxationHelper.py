from ..cashflow import Cashflow, NullCashflow
from ..cashflow.SinglePaymentFactory import Future

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

                # Can become positive tax? i.e. we gain money? 
                taxed_amount = (taxable_sum.amount - shielding_sum.amount) * self._rate
                taxes.append(Future(taxed_amount, n))
            
            return taxes
        return TaxCashflow(
            tax_fun, project._periods, 
            title=self.get_title(), shorthand="%s(%.2f%%)" % (self._tag, (self._rate * 100))
        )
 
class TaxCashflow(Cashflow):
    def __init__(self, tax_fun, d, title=None, shorthand=None):
        super().__init__(0, title)
        self._tax_fun = tax_fun
        self._d = parse_d(d)
        self._D = self._d[1] - self._d[0]
        self._shorthand = shorthand 

    def to_shorthand(self):
        return self._shorthand
    
    def cashflow_at(self, ns):
        cfs = self._tax_fun(ns)
        return cfs[0] if len(cfs) == 1 else cfs

    def to_pv(self, i):
        return sum([self[n].to_pv(i) for n in range(self._d[0], self._d[1] + 1)])

    def to_fv(self, i, n):
        return self.to_pv(i).to_fv(i, n)

    def to_av(self, i, d):
        return self.to_pv(i).to_av(i, d)
    

