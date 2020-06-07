from .Cashflow import Cashflow, PaymentScheme as ps
from . import UniformSeriesFactory as us

class Present(Cashflow):
    """
    Author: Thomas Richmond
    Description: Represents an amount of cash now.
    """

    def __init__(self, amount):
        super().__init__(amount)

    def __add__(self, other):
        return Present(self.amount + other.amount)

    def __radd__(self, other):
        if other == 0:  # first iteration of sum()
            return self
        else:
            return self.__add__(other)

    def to_pv(self, i=None):
        return self

    def to_fv(self, i, n):
        return Future(self.amount * (1 + i) ** n, i)

    def to_av(self, i, n, scheme=ps.ARREAR):
        return us.Annuity(self.amount * ((i * (1+i)**n) / ((1+i)**n) - 1), n)


class Future(Cashflow):
    """
    Author: Thomas Richmond
    Description: Represents an amount of cash in the future.
    Parameter: n [number] - The period at which the amount is received.
    """

    def __init__(self, amount, n):
        super().__init__(amount)
        self.n = n

    def to_pv(self, i):
        return Present(self.amount * (1 + i) ** (-self.n))

    def to_fv(self, n):
        if self.n == n:
            return self
        else:
            return Future(self.to_pv().amount, i, n)

    def to_av(self, i, n, scheme=ps.ARREAR):
        return us.Annuity(self.amount * i / ((1 + i)**n - 1), n)
