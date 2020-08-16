from math import log, copysign
from . import Cashflow, NullCashflow
from . import Present, Future, Annuity
from ..utilities import parse_d


class LearningCurve(Annuity):
    """
        Purpose:
            Models a continuous improvement in process as a reduction in cashflows per period.
            Uses the standard Learning Curve formula,

                C_N = C_0 * N^b;  b = log(r) / log(2)
        
            Where r is the percent learning rate per period and C_0 is the first production cost.
        Args:
            first_amount [float]
        """

    def __init__(
        self, first_amount, learning_rate, d, final_amount=None, title=None, tags=None
    ):
        super().__init__(first_amount, d, title, tags)
        self.learning_rate = float(learning_rate)
        self.b = log(self.learning_rate) / log(2.0)
        self.final_amount = final_amount

    def to_shorthand(self):
        return super().to_shorthand(["l=%f" % self.learning_rate])

    def cashflow_at(self, ns):
        cashflows = []
        for n in ns:
            if self.d[0] < n <= self.d[1]:
                year = n - self.d[0]
                amount_n = self.amount * (year) ** self.b

                if self.final_amount is not None:
                    dirn = copysign(1.0, self.final_amount - self.amount)
                    diff = amount_n - self.amount
                    if dirn * diff < 0:
                        amount_n = self.final_amount

                if n == 0:
                    cashflows.append(Present(amount_n, self.title, self.tags))
                else:
                    cashflows.append(Future(amount_n, n, self.title, self.tags))
            else:
                cashflows.append(NullCashflow())
        return cashflows[0] if len(cashflows) == 1 else cashflows

    def to_pv(self, i):
        pv = sum([cf_n.to_pv(i) for cf_n in self[self.d[0] : self.d[1] + 1]])
        return Present(pv.amount, self.title, self.tags)

    def to_fv(self, i, n):
        return self.to_pv(i).to_fv(i, n)

    def to_av(self, i, d):
        return self.to_pv(i).to_av(i, d)


class Mortgage(Annuity):
    pass
