from abc import ABC, abstractmethod

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

    @abstractmethod
    def to_pv(self):
        pass

    @abstractmethod
    def to_fv(self, i, n):
        pass

    @abstractmethod
    def to_annuity(self, i, n):
        pass
