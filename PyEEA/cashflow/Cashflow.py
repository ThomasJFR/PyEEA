from abc import ABC, abstractmethod


class Cashflow(ABC):
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
