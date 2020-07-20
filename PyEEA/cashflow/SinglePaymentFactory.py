from .Cashflow import Cashflow, NullCashflow, PaymentScheme as ps
from . import UniformSeriesFactory as us
from .utilities import parse_d

class Future(Cashflow):
    """
    Author: Thomas Richmond
    Description: Represents an amount of cash in the future.
    Parameter: n [number] - The period at which the amount is received.
    """

    def __init__(self, amount, n, title=None):
        super().__init__(amount, title)

        if type(n) is not int:
            raise ValueError("Argument n must be an integer!")
        self.n = n

    def __add__(self, other):
        if not all([isinstance(self, Future), isinstance(other, Future)]):
            return NotImplemented
        if self.n == other.n:
            val = self.amount + other.amount
            return Future(val, self.n) if self.n > 0 else Present(val)
        else:
            raise ArithmeticError(
                "Cannot add two Single cashflows occurring at different periods!"
            )

    def cashflow_at(self, ns):
        cfs = [self if n == self.n else NullCashflow() for n in ns]
        return cfs[0] if len(cfs) == 1 else cfs

    def to_shorthand(self, alt=None):
        """
        Example: -$12,000(F, 6)
        """
        return super().to_shorthand(alt or ("F", self.n))

    def to_pv(self, i):
        present_worth_factor = (1 + i) ** -self.n
        return Present(self.amount * present_worth_factor)

    def to_fv(self, i, n):
        if self.n == n:
            return self
        else:
            return self.to_pv(i).to_fv(i, n)

    def to_av(self, i, d, scheme=ps.ARREAR):
        d = us.Annuity.parse_d(d)
        D = d[1] - d[0]
        
        sinking_fund_factor = i / ((1 + i) ** D - 1)
        if d[0] == 0:
            av = self.amount * sinking_fund_factor
            return us.Annuity(av, d)
        else:
            av = self.to_pv(i).to_av(i, d)

class Present(Future):
    """
    Author: Thomas Richmond
    Description: Represents an amount of cash now, which is just the special case
                 of Future where n=0
    """

    def __init__(self, amount, title=None):
        super().__init__(amount, 0, title)

    def to_shorthand(self):
        """
        Example: $24,000(P)
        """
        return super().to_shorthand(("P"))

    def to_pv(self, i=None):
        return self

    def to_fv(self, i, n):
        compound_amount_factor = (1 + i) ** n
        return Future(self.amount * compound_amount_factor, n)

    def to_av(self, i, d, scheme=ps.ARREAR):
        d = parse_d(d)
        D = d[1] - d[0]

        capital_recovery_factor = ((i * (1 + i) ** D) / ((1 + i) ** D - 1))
        if d[0] == 0:
            av = self.amount * capital_recovery_factor
            return us.Annuity(av, d)
        else:  # We must get the "Future Present Value" and use that to compute
            # the value of our annuity.
            av = self.to_fv(i, d[0]).amount * capital_recovery_factor
            return us.Annuity(av, d)
