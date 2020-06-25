from .Cashflow import Cashflow, PaymentScheme as ps
from . import SinglePaymentFactory as sp
from . import NullCashflow as nu


class Annuity(Cashflow):
    def __init__(self, amount, d, title=None):
        super().__init__(amount, title)
        self.d = self.parse_d(d)  # The start and end period of the annuity
        self.D = self.d[1] - self.d[0]  # The number of periods for the annuity

    def cashflow_at(self, ns):
        cfs = []
        for n in ns:
            if self.d[0] < n <= self.d[1]: 
                cfs.append(sp.Future(self.amount, n))
            else:
                cfs.append(nu.NullCashflow())
        return cfs[0] if len(cfs) == 1 else cfs

    def to_shorthand(self, alt=None):
        """
        Example: -$10(A, [0, 10])
        """
        return super().to_shorthand(alt or ("A", self.d))

    def to_pv(self, i):
        pv = self.amount * ((1 + i) ** self.D - 1) / (i * (1 + i) ** self.D)

        if self.d[0] == 0:  # PV is correct
            return sp.Present(pv)
        else:  # If our annuity begins in the future, v is a FV and must
            # be converted to a PV.
            return sp.Future(pv, self.d[0]).to_pv(i)

    def to_fv(self, i, n):
        if self.d[0] == 0:  # Use standard formulas
            if self.d[1] == n:
                fv = self.amount * ((1 + i) ** n - 1) / i
                return sp.Future(fv, n)
            else:
                return self.to_pv(i).to_fv(i, n)
        else:  # Annuity is not ordinary; convert to "Future Present Value", -
            # that is, the future value at the starting period of the annuity -
            # then to Present Value, then to Future Value
            fpv = self.amount * ((1 + i) ** self.dn - 1) / (i * (1 + i) ** self.dn)
            return sp.Future(fpv, d[0]).to_pv(i).to_fv(i, n)

    def to_av(self, i, d, scheme=ps.ARREAR):
        d = self.parse_d(d)
        D = d[1] - d[0] + 1

        if d == self.d:  # The requested annuity is equivalent to this instance
            return self
        else:
            return self.to_pv(i).to_av(i, d)

    @classmethod
    def parse_d(cls, d):
        """
        Author: Thomas Richmond
        Purpose: We expect an Annuity to occur over a finite duration.
                 (for an infinite duration, refer to Perpetuity implementation)
                 This duration does not necessarily have to start at the first period,
                 so n is specified to be a list of two whole numbers, inclusively
                 indicating the start and end period for the annuity. However, it may
                 be desirable to assume n starts at one and supply a single integer value
                 to specify the end date for syntactic clarity.
                 This method is used to convert a nonspecific parameter n into a form
                 compliant with the design of the library.
        Parameter: d [any] - An integer, whole-number float or 1 or 2-element list.
                             Integers, floats and one-element lists are assumed to specify
                             the end period of an annuity starting at period one.
        Returns: A two-element list of the start and end periods of the annuity.
        """
        isint = lambda x: any([type(x) is int, type(x) is float and x // 1 == x])

        if type(d) is list:
            if len(d) == 1 and isint(d[0]):
                return [0, int(d[0])]
            elif len(d) == 2 and isint(d[0]) and isint(d[1]):
                return [int(d[0]), int(d[1])]
            else:
                raise ValueError(
                    "Argument n in list form must contain whole numbers,"
                    + "and its length must not exceed 2"
                )
        elif isint(d):
            return [0, int(d)]
        else:
            raise TypeError(
                "Type of argument n <%s> is not supported;" % type(d)
                + "must be whole number or list of whole numbers"
            )


class Gradient(Annuity):
    def __init__(self, amount, G, d, title=None):
        super().__init__(amount, d, title)
        self.G = G

    def to_shorthand(self):
        return super().to_shorthand(("G", self.d, self.G))

    def cashflow_at(self, ns):
        cfs = []
        for n in ns:
            if self.d[0] < n <= self.d[1]:
                fv = self.amount + self.G * (n - self.d[0] - 1)
                cfs.append(sp.Future(fv, n))
            else:
                cfs.append(nu.NullCashflow())
        return cfs[0] if len(cfs) == 1 else cfs

    def to_pv(self, i):
        pv1 = (
            self.amount * ((1 + i) ** self.D - 1) / (i * (1 + i) ** self.D)
        )  # Annuity Term
        pv2 = (
            self.G * ((1 + i) ** self.D - i * self.D - 1) / (i ** 2 * (1 + i) ** self.D)
        )  # Gradient Term
        pv = pv1 + pv2
        if self.d[0] == 0:  # Requested gradient is equivalet to this instance
            return sp.Present(pv)
        else:  # The gradient starts at n > 0, so we need to convert a "future present value" to a present value
            return sp.Future(pv, d[0]).to_pv(i)

    def to_fv(self, i, n):
        return self.to_pv(i).to_fv(i, n)

    def to_av(self, i, d):
        d = self.parse_d(d)
        D = d[1] - d[0] + 1

        if d == self.d and d[0] == 0:  # Use standard formula
            A_eq = self.amount + G * (1 / i - D / ((1 + i) ** n - 1))
            return Annuity(A_eq)
        else:
            return self.to_pv(i).to_av(i, d)


class Geometric(Annuity):
    def __init__(self, amount, g, d, title=None):
        super().__init__(amount, d, title)
        self.g = g

    def to_shorthand(self):
        return super().to_shorthand(("g", self.d, str(self.g * 100) + "%"))

    def cashflow_at(self, ns):
        cfs = []
        for n in ns:
            if self.d[0] < n <= self.d[1]:
                fv = self.amount * (1 + g) ** (n - self.d[0] - 1)
                cfs.append(sp.Future(fv, n))
            else:
                cfs.append(nu.NullCashflow())
        return cfs[0] if len(cfs) == 1 else cfs

    def to_pv(self, i):
        if i == self.g:
            xv = self.amount * self.D * (1 + i) ** -1

            if self.d[0] == 0:
                return sp.Present(xv)
            else:
                return sp.Future(xv, self.d[0]).to_pv(i)
        elif i > self.g:
            xv = (
                self.amount
                * (1 - (1 + self.g) ** self.D * (1 + self.g) ** -self.D)
                / (i - self.g)
            )

            if self.d[0] == 0:
                return sp.Present(xv)
            else:
                return sp.Future(xv, self.d[0]).to_pv(i)
        else:
            raise ValueError("Geometric rate (g) cannot exceed interest rate (i)!")

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


class Perpetuity(Cashflow):
    def __init__(self, amount, d0=0, title=None):
        super().__init__(amount, title)
        if type(d0) is not int:
            raise TypeError("Parameter d0 must be an integer!")
        self.d0 = d0

    def to_shorthand(self, alt=None):
        return super().to_shorthand(alt or ("A", "[{}, inf]".format(self.d0)))

    def cashflow_at(self, ns):
        cfs = []
        for n in ns:
            if n > self.d0:
                cfs.append(sp.Future(self.amount, n))
            else:
                cfs.append(nu.NullCashflow())
        return cfs[0] if len(cfs) == 1 else cfs

    def to_pv(self, i):
        xv = self.amount / i
        if self.d0 > 0:
            return sp.Future(xv, self.d0).to_pv(i)
        else:
            return sp.Present(xv)

    def to_fv(self, i, n):
        return self.to_pv(i).to_fv(i, n)

    def to_av(self, i, d):
        return self.to_pv(i).to_av(i, d)


class GeoPerpetuity(Perpetuity):
    def __init__(self, amount, g, d0=0, title=None):
        super().__init__(amount, d0, title)
        self.g = g  # Geometric rate

    def to_shorthand(self):
        return super().to_shorthand(
            ("g", "[{}, inf]".format(self.d0), str(self.g * 100) + "%")
        )

    def cashflow_at(self, ns):
        cfs = []
        for n in ns:
            if n > self.d0:
                fv = self.amount * (1 + self.g) ** (n - self.d0 - 1)
                cfs.append(sp.Future(fv, n))
            else:
                cfs.append(nu.NullCashflow())
        return cfs[0] if len(cfs) == 1 else cfs

    def to_pv(self, i):
        if i <= self.g:
            raise ValueError(
                "Geometric Perpetuity rate (g) must be greater than the interest rate (i)!"
            )

        xv = self.amount / (i - self.g)
        if self.d0 > 0:
            return sp.Future(xv, n)
        else:
            return sp.Present(xv)
