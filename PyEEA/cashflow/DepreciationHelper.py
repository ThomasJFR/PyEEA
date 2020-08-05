from collections.abc import Iterable
from abc import ABC, abstractmethod

from . import Cashflow, NullCashflow
from . import SinglePaymentFactory as sp
from . import UniformSeriesFactory as us
from .utilities import parse_d, parse_ns


class Depreciation(ABC):

    depreciation_id = 1  # Iterating counter used whenever a title isn't given
    
    def __init__(self, cashflows, d, salvage=0, title=None, tags=None):
        """
        Author: Thomas Richmond
        Purpose:
        Parameters: N [int] - The depreciable life of the product.
                    cashflows [list(Cashflow)] - A collection of single payments to be depreciated
        """
        self.d = parse_d(d)
        self.D = self.d[1] - self.d[0]
        self.salvage = salvage

        if not isinstance(cashflows, Iterable):
            cashflows = [cashflows]

        if any([True for cf in cashflows if not isinstance(cf, sp.Future)]):
            raise ValueError(
                "Depreciated cashflows can only consist of single payments occuring at the same period."
            )
        if len({cf.n for cf in cashflows}) != 1:
            raise ValueError("Depreciated cashflows must occur in the same period")
        if self.d[0] < cashflows[0].n <= self.d[1]:
            raise ValueError(
                "Depreciated cashflows are out of range of defined depreciation period!"
            )
        self.cashflows = cashflows
        self.base = sum([cf.amount for cf in cashflows])

        self.title = title or (
            "%s %i " % (self.get_depreciation_name(), Depreciation.depreciation_id)
        )

        if not tags:  # If falsey, just give an empty list
            tags = []
        elif type(tags) is str:
            tags = [tags]
        self.tags = [self.title, *tags]
        
        Depreciation.depreciation_id += 1
 
    def __getitem__(self, val):
        """
        Implemented so we can get the cashflow that occurs at period n as follows:
            my_cashflow @ 2
        For single payments, the value is zero unless the periods match
        """
        ns = parse_ns(val)
        return self.depreciation_at(ns)

    def set_title(self, title):
        self.title = title

    def get_title(self):
        return self.title

    def get_cashflows(self):
        return self.cashflows

    @abstractmethod
    def depreciation_at(self, ns):
        """
        Parameters: ns [tuple(int)] - The periods to get the value of depreciation at.
        """
        pass

    def to_pv(self, i):
        xv = sum(self.cashflows)
        return xv.to_pv(i)

    def to_fv(self, i, n):
        xv = sum(self.cashflows)
        return xv.to_fv(i, n)

    def to_av(self, i, d):
        return self.to_pv(i).to_av(i, d)
    
    @classmethod
    def get_depreciation_name(cls):
        return cls.__name__



class StraightLine(Depreciation):
    def __init__(self, cashflows, d, salvage=0, title=None, tags=None):
        super().__init__(cashflows, d, salvage, title)
        self.rate = 1 / self.D

    def depreciation_at(self, ns):
        """
        Parameters: ns [tuple(int)] - The periods to get the cashflows at.
        """
        dps = []
        for n in ns:
            if self.d[0] < n <= self.d[1]:
                expense = (self.base - self.salvage) * self.rate
                dps.append(sp.Future(expense, n))
            else:
                dps.append(NullCashflow())

        return dps[0] if len(dps) == 1 else dps

class SumOfYearsDigits(Depreciation):
    def __init_(self, cashflows, d, salvage=0, title=None, tags=None):
        super().__init__(cashflows, d, salvage, title, tags)

    def depreciation_at(self, ns):
        dps = []
        soyd = sum(range(self.D + 1))
        for n in ns:
            if self.d[0] < n <= self.d[1]:
                year = n - self.d[0]
                rate_now = (self.D - year) / soyd
                expense = self.base * rate_now
                dps.append(sp.Future(expense, n))
            else:
                dps.append(NullCashflow())

        return dps[0] if len(dps) == 1 else dps

class DecliningBalance(Depreciation):
    def __init__(self, cashflows, rate, d, salvage=0, title=None, tags=None):
        super().__init__(cashflows, d, salvage, title, tags)
        self.rate = rate

    def depreciation_at(self, ns):
        dps = []
        if self.d[0] < n <= self.d[1]:
            year = n - d[0]
            balance_now = self.base * (1 - self.rate) ** (year - 1)
            expense = balance_now * self.rate
            if n == self.d[1]:  # Final year; adjust cashflow to achieve salvage
                adjustment = (balance - expense) + self.salvage
                expense += adjustment
            dps.append(sp.Future(expense, n))
        else:
            dps.append(NullCashflow())

        return dps[0] if len(dps) == 1 else dps

