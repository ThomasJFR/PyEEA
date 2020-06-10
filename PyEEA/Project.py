from scipy.optimize import fsolve
from .cashflow import SinglePaymentFactory as sp
from .cashflow import UniformSeriesFactory as us


class Project:
    """
    Author: Thomas Richmond
    Description: A collection of revenues and costs for a project.
                 Projects serve to (i) encapsulate a set of costs,
                 (ii) enable more advanced project worth analysis, and
                 (iii) define a common interest rate for all cash flows.
    Parameters: name [string] - A human-readable name used to distinguish
                                the project from others. This is especially
                                important when exporting projects to other 
                                forms, e.g. charts or spreadsheets.
                interest [number] - The interest rate to apply to all
                                    cash flows within the project.
    """

    def __init__(self, title="generator", interest=0.12):
        self.title = title
        self.interest = interest

        self.cashflows = []
        self.periods = 0

    def __getitem__(self, val):
        if type(val) == int:
            ns = (val,)  # Get the cashflows in a period as an array
        elif type(val) == tuple:
            ns = val  # Get the cashflows of multiple periods as a 2D array
        elif type(val) == slice:
            start = val.start or 0
            stop = (val.stop if val.stop else self.periods) + 1
            step = val.step or 1
            ns = range(start, stop, step)

        cfs = [[cf @ n for cf in self.cashflows] for n in ns]
        return cfs[0] if len(cfs) == 1 else cfs

    def __add__(self, other):
        agg = Project()
        for cf1 in self.cashflows:
            agg.add_cashflow(cf1)
        for cf2 in other.cashflows:
            agg.add_cashflow(cf2)

        return agg  # The aggregation of Projects

    def __radd__(self, other):
        if other == 0:  # Happens when sum() begins
            return self
        else:
            return self.__add__(other)

    def __lt__(self, them):
        if type(them) == int or type(them) == float:
            return self.npw() < them
        else:
            return self.npw() < them.npw()

    def __le__(self, them):
        if type(them) == int or type(them) == float:
            return self.npw() <= them
        else:
            return self.npw() <= them.npw()

    def __gt__(self, them):
        if type(them) == int or type(them) == float:
            return self.npw() > them
        else:
            return self.npw() > them.npw()

    def __ge__(self, them):
        if type(them) == int or type(them) == float:
            return self.npw() >= them
        else:
            return self.npw() >= them.npw()

    def set_title(self, title):
        self.title = title

    def set_interest(self, interest):
        self.interest = interest

    """
    Author: Thomas Richmond
    Description: Adds a single cashflow to the project cashflow list.
    Parameters: cf [Cashflow] - A cashflow object
    Returns: The instance of Project, allowing for daisy-chaining
    """

    def add_cashflow(self, cf):
        if type(cf) == sp.Present:
            pass
        elif type(cf) == sp.Future:
            if cf.n > self.periods:
                self.periods = cf.n
        elif isinstance(cf, us.Annuity):
            if cf.d[1] > self.periods:
                self.periods = cf.d[1]

        self.cashflows.append(cf)
        return self  # Daisy Chaining!

    """
    Author: Thomas Richmond
    Description: Analogous in purpose to add_cashflow() above, but provides an alternate syntax
    Parameters: cfs [iterable(Cashflow)] - An iterable of cashflows which are added to the list
                                           of project cashflows.
    Returns: The instance of Project, allowing for daisy-chaining
    """

    def add_cashflows(self, cfs):
        for cf in cfs:
            self.add_cashflow(cf)
        return self

    def revenues(self):
        return [cf for cf in self.cashflows if cf.amount > 0]

    def costs(self):
        return [cf for cf in self.cashflows if cf.amount < 0]

    #################################
    ### PROJECT VALUATION FUNCTIONS
    ###

    def get_ncfs(self):
        """
        Author: Thomas Richmond
        Purpose: Gets the net cashflow for every period of the project.
        Returns: An array of net cashflows throughout the whole project
        """
        ncfs = []
        for n in range(self.periods + 1):
            cfs = self[n]  # Get the cashflows for this period
            if len(cfs) == 0:
                ncfs.append(sp.Present(0) if n == 0 else sp.Future(0, n))
                continue

            ncf = sum([cf @ n for cf in cfs]) or (
                sp.Future(0, n) if n > 0 else sp.Present(0)
            )
            ncfs.append(ncf)

        return ncfs

    def npw(self, i=None):
        if self.interest == None and i == None:
            raise ValueError(
                "No interest provided for npw calculations.\nDid you mean to use set_interest(i)?"
            )

        return sum([cf.to_pv(i or self.interest) for cf in self.cashflows])

    def bcr(self, i=None):
        if self.interest == None and i == None:
            raise ValueError(
                "No interest provided for bcr calculations. \nDid you mean to use set_interest(i)?"
            )

        pvb = sum([r.to_pv(i or self.interest) for r in self.revenues()]) or sp.Present(
            0
        )
        pvc = sum([c.to_pv(i or self.interest) for c in self.costs()]) or sp.Present(0)

        if pvc == 0:
            raise ArithmeticError("No costs in project; B/C is infinite!")

        return abs(pvb.amount / pvc.amount)

    def eucf(self, n=None):
        if n == None:
            raise NotImplementedError
        return self.npw().to_av(self.interest, n)

    def irr(self):
        # WARNING: This only gets one value of IRR, but there could be more than one...
        return fsolve(lambda i: self.npw(i).amount, self.interest)[0]

    def mirr(self, e_inv=None, e_fin=None):
        ncfs = self.get_ncfs()

        fvb = sum(
            [
                ncf.to_fv(e_fin or self.interest, self.periods)
                for ncf in ncfs
                if ncf.amount > 0
            ]
        ) or sp.Future(0, self.periods)
        pvc = sum(
            [ncf.to_pv(e_inv or self.interest) for ncf in ncfs if ncf.amount < 0]
        ) or sp.Present(0)

        return fsolve(lambda i: (fvb.to_pv(i) + pvc).amount, self.interest)[0]

    def describe():
        pass
