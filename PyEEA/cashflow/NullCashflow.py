from .Cashflow import Cashflow
from . import SinglePaymentFactory as sp
from . import UniformSeriesFactory as us

class NullCashflow(Cashflow):
    """
    Author: Thomas Richmond
    Description: A "null" cashflow - that is, a cashflow whos amount is necessarily
                 zero at every period. The cashflow has no other properties. 
                 All arithmetic operations with a NullCashflow instance return the operand.
                 This instance is generally used to explicitly indicate that a cashflow has 
                 no effect at a period, or that there are no cashflows in a period.
    """
    
    def __init__(self):
        return super().__init__(0)

    def __add__(self, other):
        return other

    def to_shorthand(self):
        return super().to_shorthand(('N',))

    def cashflow_at(self, n):
        return self

    def to_pv(self, i):
        return sp.Present(0)

    def to_fv(self, i, n):
        return sp.Future(0, n)

    def to_av(self, i, d, scheme):
        return us.Annuity(0, d)

