from abc import ABC, abstractmethod

class Cashflow(ABC):
    def __init__(self, amount, interest):
        self.amount = amount
        self.i = interest

    @abstractmethod
    def to_pv(self):
        pass

    @abstractmethod
    def to_fv(self, n):
        pass

    @abstractmethod
    def to_annuity(self, n):
        pass
