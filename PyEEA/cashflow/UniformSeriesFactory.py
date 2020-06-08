from .Cashflow import Cashflow, PaymentScheme as ps
from . import SinglePaymentFactory as sp

class Annuity(Cashflow):
    def __init__(self, amount, d):
        super().__init__(amount)
        self.d = self.parse_d(d)  # The start and end period of the annuity
        self.D = self.d[1] - self.d[0] + 1  # The number of periods for the annuity

    def __repr__(self):
        """
        Author: Thomas Richmond
        Purpose: Displays a cash amount in a pretty format.
        Example: << Present: 
        """
        return "<< {}: {}${:,.2f} for d={} >>".format(
            self.get_name(),
            '-' if self.amount < 0 else ' ',
            abs(self.amount),
            self.d)


       
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
                return [1, int(d[0])]
            elif len(d) == 2 and isint(d[0]) and isint(d[1]):
                return [int(d[0]), int(d[1])]
            else:
                raise ValueError("Argument n in list form must contain whole numbers," + \
                                 "and its length must not exceed 2")
        elif isint(d):
            return [1, int(d)]
        else:
            raise TypeError("Type of argument n <%s> is not supported;" % type(d) + \
                            "must be whole number or list of whole numbers")


    def to_pv(self, i):
        pv = self.amount * ((1 + i)**self.D - 1) / (i * (1+i)**self.D)

        if self.d[0] == 1:  # PV is correct
            return sp.Present(pv)
        else:  # If our annuity begins in the future, v is a FV and must
               # be converted to a PV.
            return sp.Future(pv, self.d[0]).to_pv(i)

    def to_fv(self, i, n):
        if self.d[0] == 1:  # Use standard formulas
            if self.d[1] == n:
                fv = self.amount * ((1 + i)**n - 1) / i
                return sp.Future(fv, n)
            else:
                return self.to_pv(i).to_fv(i, n)
        else:  # Annuity is not ordinary; convert to "Future Present Value", -
               # that is, the future value at the starting period of the annuity -
               # then to Present Value, then to Future Value
            fpv = self.amount * ((1 + i)**self.dn - 1) / (i * (1+i)**self.dn)
            return sp.Future(fpv, d[0]).to_pv(i).to_fv(i, n)
    

    def to_av(self, i, d, scheme=ps.ARREAR):
        d = self.parse_d(d)
        D = d[1] - d[0] + 1

        if d == self.d:  # The requested annuity is equivalent to this instance
            return self
        else:
            return self.to_pv(i).to_av(i, d)

class Gradient(Annuity):
    def __init__(self, amount, d, G):
        super().__init__(amount, d)
        self.G = G

    def to_pv(self, i):
        pv1 = self.amount * ((1 + i)**self.D - 1) / (i * (1+i)**self.D)  # Annuity Term
        pv2 = self.G * ((1 + i)**n - i * self.D - 1) / (i**2 * (1 + i) ** D))  # Gradient Term
        pv = pv1 + pv2
        if self.d[0] == 1:  # Requested gradient is equivalet to this instance
            return sp.Present(pv)
        else:  # The gradient starts at n > 0, so we need to convert a "future present value" to a present value
            return sp.Future(pv, d[0]).to_pv(i)

    def to_fv(self, i, n):
        return self.to_pv(i).to_fv(i, n)

    def to_av(self, i, d):
        d = self.parse_d(d)
        D = d[1] - d[0] + 1
        
        if d == self.d and d[0] == 1:  # Use standard formula
            A_eq = G * (1/i - D / ((1 + i) ** n - 1))
            return Annuity(A_eq)
        else:
            return self.to_pv(i).to_av(i, d)

class Geometric(Annuity):
    def __init__(self, amount, d, g):
        super().__init__(amount, d)
        self.g = g
    
    def to_pv(self, i):
        if i == self.g:
            xv = self.amount * self.D * (1 + i) ** -1
            
            if self.d[0] == 1:
                return sp.Present(xv)
            else:
                return sp.Future(xv, self.d[0]).to_pv(i)
        elif i > self.g:
            xv = self.amount * (1 - (1 + self.g) ** self.D * (1 + self.g) ** -self.D) / (i - self.g)

            if self.d[0] == 1:
                return sp.Present(xv)
            else
                return sp.Future(xv, self.d[0]).to_pv(i)
        else
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
    def to_pv(self, i):
        return sp.Present(self.amount / i)
    
    def to_fv(self, i, n):
        return self.to_pv(i).to_fv(i, n)

    def to_av(self, i, n):
        return self.to_pv(i).to_av(i, n)


class GPerpetuity(Cashflow):
    def __init__(self, amount, g):
        super().__init__(amount)
        self.g = g  # Geometric rate

    def to_pv(self, i):
        if i <= self.g:
            raise ValueError("Geometric Perpetuity rate (g) must be greater than the interest rate (i)!")
        return sp.Present(self.amount / (i - g))

    def to_fv(self, i, n):
        return self.to_pv(i).to_fv(i, n)

    def to_av(self, i, n, scheme=ps.ARREAR):
        av = self.to_pv(i).tO_av(i, n)  # TODO This isn't a complete implementation; it only considers n starting at 1

# TODO add more stuff...
