from .Cashflow import Cashflow, PaymentScheme as ps
from . import SinglePaymentFactory as sp

class Annuity(Cashflow):
    def __init__(self, amount, n):
        super().__init__(amount)

        if type(n) is list:
            if len(n) == 1:
                self.n = [0, int(n[0])]
            elif len(n) == 2:
                self.n = [int(n[0]), int(n[1])]
            else:
                raise ValueError("Length of argument 3 cannot exceed 2")
        else:
            self.n = [0, int(n)]

    def to_pv(self, i):
        n = (self.n[1] - self.n[0])
        v = self.amount * ((1 + i)**n - 1) / (i * (1+i)**n)

        if self.n[0] == 0: 
            return sp.Present(v)
        else:
            return sp.Future(v, self.n[0]).to_pv(i)

    def to_fv(self, i, n):
        if n == (self.n[1] - self.n[0]):
            return sp.Future(self.amount * ((1 + i)**n - 1) / i, n)
        else:
            return sp.Future(self.to_pv(i)).to_fv(i, n)

    def to_av(self, i, n, scheme=ps.ARREAR):
        if n == (self.n[1] - self.n[0] + 1):
            return self
        else:
            return self.to_pv(i).to_av(i, n)

class Gradient(Cashflow):
    pass


class Geometric(Cashflow):
    pass


class Perpetuity(Cashflow):
    pass


class GPerpetuity(Cashflow):
    pass


# TODO add more stuff...
