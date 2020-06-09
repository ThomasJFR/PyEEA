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
    
    def to_shorthand(self):
        """
        Example: $24,000(P)
        """
        return super().to_shorthand(('P'))

    def to_pv(self, i=None):
        return self

    def to_fv(self, i, n):
        return Future(self.amount * (1 + i) ** n, i)

    def to_av(self, i, d, scheme=ps.ARREAR):
        d = us.Annuity.parse_d(d)
        D = d[1] - d[0] + 1
        
        if d[0] == 1:
            av = self.amount * ((i * (1+i)**D) / ((1+i)**D) - 1)
            return us.Annuity(av, d)
        else:  # We must get the "Future Present Value" and use that to compute
               # the value of our annuity.
            fpv = self.amount * (1 + i) ** d[0]
            av = fpv * ((i * (1+i)**D) / ((1+i)**D) - 1)
            return us.Annuity(av, d)

class Future(Cashflow):
    """
    Author: Thomas Richmond
    Description: Represents an amount of cash in the future.
    Parameter: n [number] - The period at which the amount is received.
    """

    def __init__(self, amount, n):
        super().__init__(amount)
        self.n = n

    def __add__(self, other):
        if self.n == other.n:
            return Future(self.amount + other.amount, self.n)
        else:
            raise ArithmeticError("Cannot add two Future cashflows with different periods!")

    def __radd__(self, other):
        if other == 0:  # first iteration of sum()
            return self
        else:
            return self.__add__(other)

    def to_shorthand(self):
        """
        Example: -$12,000(F, 6)
        """
        return super().to_shorthand(('F', self.n))

    def to_pv(self, i):
        return Present(self.amount * (1 + i) ** (-self.n))

    def to_fv(self, i, n):
        if self.n == n:
            return self
        else:
            return self.to_pv(i).to_fv(i, n)

    def to_av(self, i, d, scheme=ps.ARREAR):
        d = Annuity.parse_d(d)
        D = d[1] - d[0] + 1
        return us.Annuity(self.amount * i / ((1 + i)**D - 1), d)
    
