from . import Cashflow
from ..utilities import parse_d, parse_ns

class Dynamic(Cashflow):
    def __init__(self, amount_fun, d, title=None, tags=None):
        super().__init__(0, title, tags)
        self._amount_fun = amount_fun
        self.d = parse_d(d)
        self.D = self.d[1] - self.d[0]

    def to_shorthand(self):
        # TODO New implementaton needed
        return "Dynamic Series"
    
    def cashflow_at(self, ns):
        ns = parse_ns(ns)
        cashflows = []
        for n in ns:
            cashflows.append(self._amount_fun(self, n))
        return cashflows[0] if len(cashflows) == 1 else cashflows

    def to_pv(self, i):
        return sum([self[n].to_pv(i) for n in range(self.d[0], self.d[1] + 1)])

    def to_fv(self, i, n):
        return self.to_pv(i).to_fv(i, n)

    def to_av(self, i, d):
        return self.to_pv(i).to_av(i, d)
