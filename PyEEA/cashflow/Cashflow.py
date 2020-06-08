from abc import ABC, abstractmethod
from enum import Enum


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
        rstring = "{}${:,.2f}".format(
                  '-' if self.amount < 0 else ' ',
                  abs(self.amount))
        return rstring + "{}"

    @classmethod
    def get_name(cls):
        return cls.__name__

    @abstractmethod
    def to_pv(self, i):
        pass

    @abstractmethod
    def to_fv(self, i, n):
        pass

    @abstractmethod
    def to_av(self, i, d, scheme):
        pass

