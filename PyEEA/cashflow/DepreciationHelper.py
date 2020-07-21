from collections.abc import Iterable
from abc import ABC, abstractmethod

from . import Cashflow, NullCashflow
from . import SinglePaymentFactory as sp
from . import UniformSeriesFactory as us
from .utilities import parse_d, parse_ns

class Depreciation(ABC):
    def __init__(self, d, cashflows, salvage=0, title=None):
        """
        Author: Thomas Richmond
        Purpose:
        Parameters: N [int] - The depreciable life of the product.
                    cashflows [list(Cashflow)] - A collection of single payments to be depreciated
        """
        self.d = parse_d(d)
        self.D = self.d[1] - self.d[0]
        self.salvage = salvage
        self.title = title
        
        if not isinstance(cashflows, Iterable):
            cashflows = [cashflows]
        
        if any([True for cf in cashflows if not isinstance(cf, sp.Future)]):
            raise ValueError("Depreciated cashflows can only consist of single payments occuring at the same period.")
        if len({cf.n for cf in cashflows}) != 1:
            raise ValueError("Depreciated cashflows must occur in the same period")
        if self.d[0] < cashflows[0].n <= self.d[1]:
            raise ValueError("Depreciated cashflows are out of range of defined depreciation period!")
        self.cashflows = cashflows
        self.base = sum([cf.amount for cf in self.cashflows])

    def __getitem__(self, val):
        """
        Implemented so we can get the cashflow that occurs at period n as follows:
            my_cashflow @ 2
        For single payments, the value is zero unless the periods match
        """
        ns = parse_ns(val)
        return self.cashflow_at(ns)

    @abstractmethod
    def cashflow_at(self, ns):
        """
        Parameters: ns [tuple(int)] - The periods to get the cashflows at.
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

class StraightLine(Depreciation):
    def __init__(self, d, cashflows, salvage=0, title=None):
        super().__init__(d, cashflows, salvage, title)
        self.annual_expense = (self.base - self.salvage) / N

    def cashflow_at(self, ns):
        """
        Parameters: ns [tuple(int)] - The periods to get the cashflows at.
        """
        cfs = []
        for n in ns:
            if self.d[0] < n <= self.d[1]:        
                remaining = self.base - annual_expense * (n - self.d[0])
                cfs.append(sp.Future(remaining, n))
            else:
                cfs.append(NullCashflow())
        
        return cfs[0] if len(cfs) == 1 else cfs



class SumOfYearsDigits(Depreciation):
    def __init_(self, d, cashflows, salvage=0, title=None):
        super().__init__(d, cashflows, salvage, title)

    def cashflow_at(self, ns):
        cfs = []
        soyd = sum(range(self.D))
        for n in ns:
            if self.d[0] < n <= self.d[1]:
                year = n - self.d[0]
                rate = (self.D - year) / soyd
                value = self.base * rate
                cfs.append(sp.Future(value, n))
            else:
                cfs.append(NullCashflow())

class DoubleDecliningBalance(Depreciation):
    def __init__(self, rate, d, cashflows, salvage=0, title=None):
        super().__init__(d, cashflows, salvage, title)
        self.rate = rate 

    def cashflow_at(self, ns):
        cfs = []
        for n in ns:
            if self.d[0] < n <= self.d[1]:
                balance = self.base * (1 - self.rate)**(n - self.d[0] - 1)
                expense = balance * self.rate
                if n == self.d[1]:
                    adjustment = (balance - expense) + self.salvage
                    expense += adjustment  # Final year; adjust cashflow to achieve salvage  
                
                if n == 0:
                    cfs.append(sp.Present(expense))
                else:
                    cfs.append(sp.Future(expense, n))
            else:
                cfs.append(NullCashflow())

        return cfs[0] if len(cfs) == 1 else cfs
"""
class CapitalCostAllowance(DoubleDecliningBalance):
    def __init__(self, rate, ucc_class)
        pass
    
    def cashflow_at(self, ns):
        cfs = []
        for n in ns:
            if self.d[0] < n <= self.d[1]:
                balance = 0
                for i in range(n + 1):
                    purchases = sum([cf[i].amount for cf in self.cashflows if cf[i].amount < 0])
                    additions = purchases

                    dispositions = sum([cf[i].amount for cf in self.cashflows if cf[i].amount > 0])
                    
                    ucc = 0
            else:
                cfs.append(cashflows)

"""
