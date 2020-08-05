from . import Cashflow
from ..utilities import parse_d

class Dynamic(Cashflow):
    def __init__(self, amount_fun, d, title=None, tags=None):
        super().__init__(0, title, tags)
        self._amount_fun = amount_fun
        self._d = parse_d(d)
        self._D = self._d[1] - self._d[0]

    def to_shorthand(self):
        # TODO New implementaton needed
        return super().to_shorthand()
    
    def cashflow_at(self, ns):
        cashflows = self._amount_fun(ns)
        return cashflows[0] if len(cashflows) == 1 else cashflows

    def to_pv(self, i):
        return sum([self[n].to_pv(i) for n in range(self._d[0], self._d[1] + 1)])

    def to_fv(self, i, n):
        return self.to_pv(i).to_fv(i, n)

    def to_av(self, i, d):
        return self.to_pv(i).to_av(i, d)