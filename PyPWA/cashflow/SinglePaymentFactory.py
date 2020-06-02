from .Cashflow import Cashflow


class Present(Cashflow):
    def __init__(self, amount, i):
        super().__init__(amount, i)

    def to_pv(self):
        return self

    def to_fv(self, n):
        return Future(self.amount * (1 + self.i) ** n, i)

    def to_annuity(self, n):
        pass


class Future(Cashflow):
    def __init__(self, amount, i, n):
        super().__init__(amount, i)
        self.n = n

    def to_pv(self):
        return Present(self.amount * (1 + self.i) ** (-self.n), self.i)

    def to_fv(self, n):
        if self.n == n:
            return self
        else:
            return Future(self.to_pv().amount, self.i, n)

    def to_annuity(self, n):
        pass  # TODO
