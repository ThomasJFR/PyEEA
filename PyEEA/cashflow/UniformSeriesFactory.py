from .Cashflow import Cashflow, NullCashflow
from . import SinglePaymentFactory as sp
from ..utilities import parse_d
from math import inf

class Annuity(Cashflow):
    def __init__(self, amount, d, title=None, tags=None):
        super().__init__(amount, title, tags)
        self.d = parse_d(d)  # The start and end period of the annuity
        self.D = self.d[1] - self.d[0]  # The number of periods for the annuity

    def __add__(self, other):
        if not all([type(self) == Annuity, type(other) == Annuity]):
            return NotImplemented
        if self.d == other.d:
            val = self.amount + other.amount
            return Annuity(val, self.d, self.title, self.tags)
        else:
            return ValueError("Added annuities must have equal durations")

    def cashflow_at(self, ns):
        cfs = []
        for n in ns:
            if self.d[0] < n <= self.d[1]:
                cfs.append(sp.Future(self.amount, n, self.title, self.tags))
            else:
                cfs.append(NullCashflow())
        return cfs[0] if len(cfs) == 1 else cfs

    def __repr__(self, alt=None):
        info = alt or ['A', self.d]
        return super().__repr__(info)

    def to_pv(self, i):
        if i == 0:
            pv = self.amount * self.D
        else:
            present_worth_factor = ((1 + i) ** self.D - 1) / (i * (1 + i) ** self.D)
            pv = self.amount * present_worth_factor

        if self.d[0] == 0:  # PV is correct
            return sp.Present(pv, self.title, self.tags)
        else:  # If our annuity begins in the future, v is a FV and must
            # be converted to a PV.
            return sp.Future(pv, self.d[0], self.title, self.tags).to_pv(i)

    def to_fv(self, i, n):
        if self.d[0] == 0:  # Use standard formulas
            if self.d[1] == n:
                fv = self.amount * ((1 + i) ** n - 1) / i
                return sp.Future(fv, n, self.title, self.tags)
            else:
                return self.to_pv(i).to_fv(i, n)
        else:  # Annuity is not ordinary; convert to "Future Present Value", -
            # that is, the future value at the starting period of the annuity -
            # then to Present Value, then to Future Value
            fpv = self.amount * ((1 + i) ** self.dn - 1) / (i * (1 + i) ** self.dn)
            return sp.Future(fpv, d[0], self.title, self.tags).to_pv(i).to_fv(i, n)

    def to_av(self, i, d):
        d = parse_d(d)
        D = d[1] - d[0]

        if d == self.d:  # The requested annuity is equivalent to this instance
            return self
        else:
            return self.to_pv(i).to_av(i, d)


class Gradient(Annuity):
    def __init__(self, amount, G, d, title=None, tags=None):
        super().__init__(amount, d, title, tags)
        self.G = G

    def __repr__(self):
        info = ['G', self.G, self.d]
        return super().__repr__(info)

    def cashflow_at(self, ns):
        cfs = []
        for n in ns:
            if self.d[0] < n <= self.d[1]:
                fv = self.amount + self.G * (n - self.d[0] - 1)
                cfs.append(sp.Future(fv, n, self.title, self.tags))
            else:
                cfs.append(NullCashflow())
        return cfs[0] if len(cfs) == 1 else cfs

    def to_pv(self, i):
        # Annual Present Worth Factor
        apwf = self.D if i == 0 else ((1 + i) ** self.D - 1) / (i * (1 + i) ** self.D)

        # Gradient Present Worth Factor
        gpwf = (
            (self.D ** 2 - self.D) / 2
            if i == 0
            else ((1 + i) ** self.D - i * self.D - 1) / (i ** 2 * (1 + i) ** self.D)
        )

        pv = self.amount * apwf + self.G * gpwf
        if self.d[0] == 0:  # Requested gradient is equivalet to this instance
            return sp.Present(pv, self.title, self.tags)
        else:  # The gradient starts at n > 0, so we need to convert a "future present value" to a present value
            return sp.Future(pv, d[0], self.title, self.tags).to_pv(i)

    def to_fv(self, i, n):
        return self.to_pv(i).to_fv(i, n)

    def to_av(self, i, d):
        d = parse_d(d)
        D = d[1] - d[0]

        if d == self.d and d[0] == 0:  # Use standard formula
            A_eq = self.amount + self.G * (1 / i - D / ((1 + i) ** (D - d[0]) - 1))
            return Annuity(A_eq, d, self.title, self.tags)
        else:
            return self.to_pv(i).to_av(i, d)


class Geometric(Annuity):
    def __init__(self, amount, g, d, title=None, tags=None):
        super().__init__(amount, d, title, tags)
        self.g = g

    def cashflow_at(self, ns):
        cfs = []
        for n in ns:
            if self.d[0] < n <= self.d[1]:
                fv = self.amount * (1 + self.g) ** (n - self.d[0] - 1)
                cfs.append(sp.Future(fv, n, self.title, self.tags))
            else:
                cfs.append(NullCashflow())
        return cfs[0] if len(cfs) == 1 else cfs

    def to_pv(self, i):
        if i == self.g:
            xv = self.amount * self.D * (1 + i) ** -1

            if self.d[0] == 0:
                return sp.Present(xv, self.title, self.tags)
            else:
                return sp.Future(xv, self.d[0], self.title, self.tags).to_pv(i)
        else:
            xv = (
                self.amount
                * (1 - (1 + self.g) ** self.D * (1 + i) ** -self.D)
                / (i - self.g)
            )

            if self.d[0] == 0:
                return sp.Present(xv, self.title, self.tags)
            else:
                return sp.Future(xv, self.d[0], self.title, self.tags).to_pv(i)
        # else:
        #   raise ValueError("Geometric rate (g) cannot exceed interest rate (i)!")

    def to_fv(self, i, n):
        """if i == self.g:
           pass
        elif i > self.g:
            if self.d[0] == 1:
                if d == self.d:
                    fv = self.amount * ((1 + i)**n - (1 + g)**n)/(i-g)
                    return sp.Future(fv, n)
                else:
                    return self.to_pv(i).to_fv(i, n)
            else:
        """
        return self.to_pv(i).to_fv(i, n)

    def to_av(self, i, d):
        return self.to_pv(i).to_av(i, d)

    def __repr__(self):
        info = ["g", str(self.g * 100) + "%", self.d]
        return super().__repr__(info)

class Perpetuity(Annuity):
    def __init__(self, amount, d0=0, title=None, tags=None):
        super().__init__(amount, [d0, inf], title, tags)

    def __add__(self, other):
        if not all([type(self) == Perpetuity, type(other) == Perpetuity]):
            raise TypeError("Perpetuities can only be added to other Perpetuities!")
        if self.d != other.d:
            return ValueError("Summed Perpetuities must have equal lifetimes d!")
        else:
            val = self.amount + other.amount
            return Perpetuity(val, self.d)

    def to_pv(self, i):
        xv = self.amount / i
        if self.d[0] > 0:
            return sp.Future(xv, self.d[0], self.title, self.tags).to_pv(i)
        else:
            return sp.Present(xv, self.title, self.tags)

    def to_fv(self, i, n):
        return self.to_pv(i).to_fv(i, n)

    def to_av(self, i, d):
        return self.to_pv(i).to_av(i, d)


class GeoPerpetuity(Geometric):
    def __init__(self, amount, g, d0=0, title=None, tags=None):
        super().__init__(amount, g, [d0, inf], title, tags)

    def to_pv(self, i):
        if i <= self.g:
            raise ValueError(
                "Geometric Perpetuity rate (g) must be greater than the interest rate (i)!"
            )

        xv = self.amount / (i - self.g)
        if self.d[0] > 0:
            return sp.Future(xv, n, self.title, self.tags)
        else:
            return sp.Present(xv, self.title, self.tags)
