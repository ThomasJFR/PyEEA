from abc import ABC, abstractmethod
from enum import Enum
from collections.abc import Iterable


class PaymentScheme(Enum):
    ARREAR = "payment in arrear"
    DUE = "payment in due"


class Cashflow(ABC):
    """
    Author: Thomas Richmond
    Description: Abstract defintion of a cashflow. All cashflows must extend
                 this definition and implement its conversion functions.
    Parameters: amount [number] - The characteristic value of the cash flow.
                                  Can be thought of the multiplier to the 
                                  characteristic interest factor of the cash flow.
                                  (e.g. < amount * (P|F, i, n) >)
    """

    def __init__(self, amount):
        self.amount = amount

    def __str__(self):
        """
        Author: Thomas Richmond
        Purpose: Displays a cash amount in a pretty format.
                 To display any additional info in children,
                 overwrite this function 
        Example: -$12,600,120.12(STUFF)
        """
        return self.to_shorthand()  # This will call from the context of the child.

    def __radd__(self, other):
        if other == 0:  # first iteration of sum()
            return self
        else:
            return self.__add__(other)

    def __getitem__(self, val):
        """
        Implemented so we can get the cashflow that occurs at period n as follows:
            my_cashflow @ 2
        For single payments, the value is zero unless the periods match
        """
        if type(val) == int:
            ns = (val,)  # Get the cashflows in a period as an array
        elif type(val) == tuple:
            ns = val  # Get the cashflows of multiple periods as a 2D array
        elif type(val) == slice:
            start = val.start or 0
            stop = val.stop + 1
            step = val.step or 1
            ns = range(start, stop, step)

        return self.cashflow_at(ns)

    def to_shorthand(self, info):
        # Step 1: Add the cash amount
        # EXAMPLE: -$12,229,999.99
        valstr = "{}${:,.2f}".format("-" if self.amount < 0 else " ", abs(self.amount))

        # Step 2: Add notated information
        # EXAMPLE: (G, [2,5], 210)
        info = (
            info if isinstance(info, Iterable) else [info]
        )  # Make info iterable if it isn't
        infostr = "(" + ", ".join([str(i) for i in info]) + ")"

        return valstr + infostr

    @abstractmethod
    def cashflow_at(self, ns):
        """
        Parameters: ns [tuple(int)] - The periods to get the cashflows at.
        """
        pass

    @abstractmethod
    def to_pv(self, i):
        pass

    @abstractmethod
    def to_fv(self, i, n):
        pass

    @abstractmethod
    def to_av(self, i, d, scheme):
        pass

    @classmethod
    def get_name(cls):
        return cls.__name__
