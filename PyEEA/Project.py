from scipy.optimize import fsolve
from .cashflow import SinglePaymentFactory as sp
from .cashflow import UniformSeriesFactory as us
from .cashflow import DepreciationHelper as dh
from .cashflow import Cashflow, NullCashflow
from .cashflow.utilities import parse_d, parse_ns


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

    def __init__(self, title=None, interest=0):
        self.title = title
        self.interest = interest

        self.cashflows = []
        self.periods = 0

    def __getitem__(self, val):
        if type(val) is str:
            matches = [cf for cf in self.cashflows if cf.title == val] or [None]
            return matches[0] if len(matches) == 1 else matches
        else:  # A numeric index
            ns = parse_ns(val)
            cfs_in_period = lambda n: [
                cf
                for cf in self.cashflows
                if any(
                    [
                        isinstance(cf, sp.Future) and n == cf.n,
                        isinstance(cf, us.Annuity) and cf.d[0] < n <= cf.d[1],
                        isinstance(cf, us.Perpetuity) and n > cf.d0,
                        isinstance(cf, dh.Depreciation) and n == cf.d[0] # USE IF PAID IN ARREAR < n <= cf.d[1],
                    ]
                )
            ]
            cfs = [[cf[n] for cf in cfs_in_period(n)] or [NullCashflow()] for n in ns]
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

    def __enter__(self):
        from copy import deepcopy

        self.cashflows_copy = deepcopy(self.cashflows)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cashflows = self.cashflows_copy
        del self.cashflows_copy

    def set_title(self, title):
        self.title = title

    def get_title(self):
        return self.title or "Project with {} cashflows".format(len(self.cashflows))

    def set_interest(self, interest):
        self.interest = interest

    def get_cashflows(self):
        return self.cashflows

    def add_cashflow(self, cf):
        """
        Author: Thomas Richmond
        Description: Adds a single cashflow to the project cashflow list.
        Parameters: cf [Cashflow] - A cashflow object
        Returns: The instance of Project, allowing for daisy-chaining
        """
        if type(cf) == sp.Present:
            pass
        elif type(cf) == sp.Future:
            if cf.n > self.periods:
                self.periods = cf.n
        elif isinstance(cf, us.Annuity):
            if cf.d[1] > self.periods:
                self.periods = cf.d[1]
        elif isinstance(cf, dh.Depreciation):
            if cf.d[1] > self.periods:
                self.periods = cf.d[1]
        self.cashflows.append(cf)
        return self  # Daisy Chaining!

    def add_cashflows(self, cfs):
        """
        Author: Thomas Richmond
        Description: Analogous in purpose to add_cashflow() above, but provides an alternate syntax
        Parameters: cfs [iterable(Cashflow)] - An iterable of cashflows which are added to the list
                                               of project cashflows.
        Returns: The instance of Project, allowing for daisy-chaining
        """
        for cf in cfs:
            self.add_cashflow(cf)

        return self

    def revenues(self):
        revenues = []
        for cf in self.cashflows:
            if isinstance(cf, Cashflow):
                if cf.amount > 0:
                    revenues.append(cf)
            if isinstance(cf, dh.Depreciation):
                if cf.base > 0:
                    revenues.append(cf)

        return revenues

    def costs(self):
        costs = []
        for cf in self.cashflows:
            if isinstance(cf, Cashflow):
                if cf.amount < 0:
                    costs.append(cf)
            if isinstance(cf, dh.Depreciation):
                if cf.base < 0:
                    costs.append(cf)

        return costs

    def to_dataframe(self, n=None):
        import pandas as pd

        periods = list(range((n or self.periods) + 1))
        titles = [cf.get_title() for cf in self.cashflows]
        cashflows = [[cf[n] for cf in self.cashflows] for n in periods]

        return pd.DataFrame(cashflows, index=periods, columns=titles)

    def to_cashflowdiagram(self, n=None, size=None):
        import pandas as pd
        from matplotlib import pyplot as plt

        periods = list(range((n or self.periods) + 1))
        titles = [cf.get_title() for cf in self.cashflows]
        cashflows = [[cf[n].amount for cf in self.cashflows] for n in periods]

        plotdata = pd.DataFrame(cashflows, index=periods, columns=titles)
        plotdata.plot(kind="bar", stacked="true")
        plt.title(self.get_title())
        plt.ylabel("USD")
        plt.xlabel("Period")

        if size:
            fig = plt.gcf()
            fig.set_size_inches(size)

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
                ncfs.append(NullCashflow())
                continue

            ncf = sum([cf[n] for cf in cfs]) or NullCashflow()
            ncfs.append(ncf)

        return ncfs

    def pbp(self):
        """
        Purpose: Get the payback period for the project.
                 Does not account for time value of money.
        """
        cfsum = 0
        for n in range(self.periods + 1):
            cfsum += sum(cf.amount for cf in self[n])
            if cfsum > 0:
                return n
        return -1

    def npw(self, i=None):
        if i is None and self.interest is None:
            raise ValueError(
                "No interest provided for npw calculations.\nDid you mean to use set_interest(i)?"
            )

        return sum([cf.to_pv(i or self.interest) for cf in self.cashflows])

    def nfw(self, n, i=None):
        return self.npw().to_fv(i or self.interest, n)

    def bcr(self, i=None):
        if self.interest == None and i == None:
            raise ValueError(
                "No interest provided for bcr calculations. \nDid you mean to use set_interest(i)?"
            )

        pvb, pvc = 0, 0
        for n in range(self.periods + 1):
            for cf in self[n]:
                amt = cf.to_pv(i or self.interest).amount
                if amt > 0:
                    pvb += amt
                else:
                    pvc += amt

        if pvb == 0 or pvc == 0:
            return 0

        return abs(pvb / pvc)

    def eacf(self, d=None):
        d = parse_d(d or self.periods)
        return self.npw().to_av(self.interest, d)

    def irr(self, *, return_all=False, default=None):
        if not all(
            [  # Make sure we have both positive and negative net cashflows; else, IRR doesn't exist
                any([ncf.amount > 0 for ncf in self.get_ncfs()]),
                any([ncf.amount < 0 for ncf in self.get_ncfs()]),
            ]
        ):
            return default

        def irr_fun(i):
            return self.npw(i[0]).amount

        irrs = fsolve(irr_fun, self.interest, factor=0.1)
        return irrs if return_all is True else irrs[0]

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

        return fsolve(lambda i: (fvb.to_pv(i) + pvc).amount, self.interest, factor=0.1)[
            0
        ]

    def describe():
        pass
