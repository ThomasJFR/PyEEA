from .Cashflow import Cashflow


class Present(Cashflow):
    def __init__(self, amount):
        super().__init__(amount)

    def to_pv(self, i=None):
        return self

    def to_fv(self, i, n):
        return Future(self.amount * (1 + i) ** n, i)

    def to_annuity(self, i, n):
        pass


class Future(Cashflow):
    def __init__(self, amount, n):
        super().__init__(amount)
        self.n = n

    def to_pv(self, i):
        return Present(self.amount * (1 + i) ** (-self.n))

    def to_fv(self, n):
        if self.n == n:
            return self
        else:
            return Future(self.to_pv().amount, i, n)

    def to_annuity(self, n):
        pass  # TODO
