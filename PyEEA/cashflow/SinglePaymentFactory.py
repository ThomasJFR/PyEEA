from .Cashflow import Cashflow, NullCashflow
from .UniformSeriesFactory import Annuity
from ..utilities import parse_d
from numbers import Number


class Future(Cashflow):
    """ A single payment made sometime in the future

    Represents a single payment made at the start of the period 
    specified by n. For example, a transfer in of amount 1000 made in
    period 3 can be represented by the following cashflow diagram:

                                ^  1000
                                |
                                |
        0 --- 1 --- 2 --- 3 --- 4 --- 5 --- 6 --- 

    
    The period n is encoded as an integer and must be finite. 

    Attributes:
        amount: The cash payment made
        n: An integer period at which the payment is made
    
    See Also:
        Present: Special case for n=0
        Cashflow: Parent class
    """

    def __init__(self, amount, n, title=None, tags=None):
        super().__init__(amount, title, tags)
        self.n = int(n)

    def cashflow_at(self, ns):
        """ See base class """
        cfs = [self if self.n == n else NullCashflow() for n in ns]
        return cfs[0] if len(cfs) == 1 else cfs

    def to_pv(self, i):
        """ See base class """
        present_worth_factor = (1 + i) ** -self.n
        present_value = self.amount * present_worth_factor
        return Present(present_value, self.title, self.tags)

    def to_fv(self, i, n):
        """ See base class """
        future_worth_factor = (1 + i) ** (n - self.n)
        future_value = self.amount * future_worth_factor
        return Future(future_value, n, self.title, self.tags)

    def to_av(self, i, d):
        """ See base class """
        d = parse_d(d)
        D = d[1] - d[0]
        if D == 0:
            raise ValueError("Annuity duration must be greater than zero years")

        sinking_fund_factor = i / ((1 + i)**D - 1)     # Converts Future at n to an Annuity over [n, n + D]
        future_worth_factor = (1 + i) ** (d[0] - self.n)  # Converts Annuity starting over [n, n+D] to Annuity over d
        annuity_value = self.amount * sinking_fund_factor * future_worth_factor 
        return Annuity(annuity_value, d, self.title, self.tags)

    def __repr__(self, info=None):
        """ See base class """
        info = info or ('F', self.n)
        return super().__repr__(info)
    
    def __add__(self, other):
        """ Sums two Future payments occurring at the same period

        Two Future instances with the same period n have their amounts
        summed to generate an equivalent single Future instance.

        Args:
            other: A second Future instance to be added to this one

        Returns:
            A new Future instance whose amount is the sum of the arguments.
        """
        if not isinstance(other, Future):
            return NotImplemented
            #raise TypeError(
            #    "Can only sum Future instance with another Future instance"
            #    "having the same period n!")
        if self.n != other.n:
            raise ValueError(
                "Future instances being added must have the same period n!")
        
        val = self.amount + other.amount
        return Future(val, self.n, self.title, self.tags)

    def __neg__(self):
        """ Inverts the sign of payment amount """
        return Future(-self.amount, self.n, self.title, self.tags)

    def __sub__(self, other):
        """ Subtraction of two Future payments occurring at the same period """
        return self.__add__(-other)

    def __mul__(self, other):
        """ Multiplies amount by a scalar """
        if isinstance(other, Number):
            return Future(self.amount * other, self.n, self.title, self.tags)

    def __lt__(self, them):
        them = them.amount if isinstance(them, Future) else float(them)
        return self.amount < them

    def __le__(self, them):
        them = them.amount if isinstance(them, Future) else float(them)
        return self.amount <= them

    def __gt__(self, them):
        return not self.__le__(them)

    def __ge__(self, them):
        return not self.__lt__(them)

class Present(Future):
    """ A single payment made now

    Represents a single payment made immediately; this is the special case of
    Future where n = 0. For example, a transfer out of amount 3250 now can be 
    represented by the following cashflow diagram:

        0 --- 1 --- 2 --- 3 --- 4 --- 5 --- 6 --- 
        |
        |
        |
        v -3250
    
    Attributes:
        amount: The cash transferred
    
    See Also:
        Future: Parent class
    """

    def __init__(self, amount, title=None, tags=None):
        super().__init__(amount, 0, title, tags)

    def to_pv(self, i=None):
        """ See base class """
        return self

    def to_fv(self, i, n):
        """ See base class """
        compound_amount_factor = (1 + i) ** n  # Converts present to Future at n
        future_value = self.amount * compound_amount_factor
        return Future(future_value, n, self.title, self.tags)

    def to_av(self, i, d):
        """ See base class """
        d = parse_d(d)
        D = d[1] - d[0]
        if D == 0:
            raise ValueError("Annuity duration must be greater than zero years")
        
        future_worth_factor = (1 + i) ** d[0]  # Converts self to Future at d[0]
        capital_recovery_factor = i * (1 + i) ** D / ((1 + i) ** D - 1)  # Converts Future at d[0] to annuity over d
        annuity_value = self.amount * future_worth_factor * capital_recovery_factor
        return Annuity(annuity_value, d, self.title, self.tags)
   
    def __repr__(self):
        """ See base class """
        info = ('P',)
        return super().__repr__(info)
    
    def __add__(self, other):
        """ Sums two Present payments

        Two Present instances have their amounts summed to generate an equivalent 
        single Present instance.

        Args:
            other: A second Present instance to be added to this one

        Returns:
            A new Present instance whose amount is the sum of the arguments.
        """
        if not isinstance(other, Present):
            return NotImplemented  #("Can only sum Present instance with another Present instance!")
        val = self.amount + other.amount
        return Present(val)


    def __mul__(self, other):
        if isinstance(other, Number):
            return Present(self.amount * other, self.title, self.tags)

