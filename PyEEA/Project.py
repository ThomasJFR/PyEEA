from scipy.optimize import fsolve

from .cashflow import Cashflow, NullCashflow
from .cashflow import SinglePaymentFactory as sp
from .cashflow import UniformSeriesFactory as us

from .taxation import TaxationHelper as th, DepreciationHelper as dh

from .utilities import parse_d, parse_ns


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
        self._title = title
        self._interest = interest

        self._cashflows = []
        self._depreciations = []
        self._taxes = []
        
        self._periods = 0

    def __str__(self):
        return self.to_dataframe().to_string()

    def __getitem__(self, val):
        # OPTION 1: Index by tags
        if type(val) is str:
            matches = [cf for cf in self.get_cashflows() if val in cf.tags]
            return matches
        # OPTION 2: Index by periods
        else: 
            if type(val) == int:
                ns = (val,)  # Get the cashflows in a period as an array
            elif type(val) == tuple:
                ns = val  # Get the cashflows of multiple periods as a 2D array
            elif type(val) == slice:
                start = val.start or 0
                stop = (val.stop or self._periods) + 1
                step = val.step or 1
                ns = range(start, stop, step)

            def get_cashflows_for_period(n):
                def do_include_cashflow(cf):
                    return any([
                        isinstance(cf, sp.Future) and n == cf.n,
                        isinstance(cf, us.Annuity) and cf.d[0] < n <= cf.d[1],
                        isinstance(cf, us.Perpetuity) and n > cf.d0,
                    ])
                return [cf for cf in self.get_cashflows() if do_include_cashflow(cf)]
            
            cashflows = [[cf[n] for cf in get_cashflows_for_period(n)] for n in ns]
            return cashflows

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

        self._cashflows_copy = deepcopy(self._cashflows)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cashflows = self._cashflows_copy
        del self._cashflows_copy

    def set_title(self, title):
        self._title = title

    def get_title(self):
        return self._title or "Project with {} cashflows".format(len(self.get_cashflows()))

    def set_interest(self, interest):
        self._interest = interest

    def add_cashflow(self, cashflow):
        """
        Author: Thomas Richmond
        Description: Adds a single cashflow to the project cashflow list.
        Parameters: cf [Cashflow] - A cashflow object
        Returns: The instance of Project, allowing for daisy-chaining
        """

        if not isinstance(cashflow, Cashflow):
            raise TypeError("Argument must be a child of Cashflow")

        self._cashflows.append(cashflow)

        def final_period(cf):
            if isinstance(cf, sp.Future):  # Also accounts for Present
                return cf.n
            elif isinstance(cf, us.Annuity):
                return cf.d[1]
            else:
                return 0

        # Update our periods if needed
        nf = final_period(cashflow)
        if nf > self._periods:
            self._periods = nf

        return self  # Daisy Chaining!

    def add_depreciation(self, depreciation):
        if not isinstance(depreciation, dh.Depreciation):
            raise TypeError("Argument must be a child of Depreciation")
        
        self._depreciations.append(depreciation)
        self.add_cashflows(depreciation.cashflows)

        if depreciation.d[1] > self._periods:
            self._periods = depreciation.d[1]
        
        return self 

    def add_cashflows(self, cashflows):
        """
        Author: Thomas Richmond
        Description: Analogous in purpose to add_cashflow() above, but provides an alternate syntax
        Parameters: cfs [iterable(Cashflow)] - An iterable of cashflows which are added to the list
                                               of project cashflows.
        Returns: The instance of Project, allowing for daisy-chaining
        """
        for cashflow in cashflows:
            if isinstance(cashflow, Cashflow):
                self.add_cashflow(cashflow)
            elif isinstance(cashflow, dh.Depreciation):
                self.add_depreciation(cashflow)
            else:
                raise TypeError("Cashflow type was not recognized!")

        return self

    def get_cashflows(self):
        return self._cashflows

    def get_depreciations(self):
        return self._depreciations

    def add_tax(self, tax):
        """
        Purpose:
            Adds cashflows to the project representing taxes.
            TODO Takes into account tax shields generated by depreciation 
        Args:
            tag [string] - Cashflows with a matching tag will be taxed
            rate [float] - A percent interest rate to apply
        """
        if not isinstance(tax, th.Tax):
            raise TypeError("Argument must be a Tax instance!")
        
        self._taxes.append(tax)

        return self

    def add_taxes(self, taxes):
        for tax in taxes:
            self.add_tax(tax)
        return self

    def get_taxes(self):
        return self._taxes 

    def get_taxflows(self):
        return [tax.generate_cashflow(self) for tax in self.get_taxes()]

    def get_taxed_cashflows(self):
        return self.get_cashflows() + self.get_taxflows()

    def revenues(self):
        revenues = []
        for cf in self.get_cashflows():
            if isinstance(cf, Cashflow):
                if cf.amount > 0:
                    revenues.append(cf)
        return revenues

    def costs(self):
        costs = []
        for cf in self.get_cashflows():
            if isinstance(cf, Cashflow):
                if cf.amount < 0:
                    costs.append(cf)
        return costs


    def to_dataframe(self, n=None):
        import pandas as pd

        periods = list(range((n or self._periods) + 1))
        titles = [cf.get_title() for cf in self.get_taxed_cashflows()]
        cashflows = [[cf[n] for cf in self.get_taxed_cashflows()] for n in periods]
        
        return pd.DataFrame(cashflows, index=periods, columns=titles)

    def to_cashflowdiagram(self, n=None, size=None):
        import pandas as pd
        from matplotlib import pyplot as plt

        periods = list(range((n or self._periods) + 1))
        titles = [cf.get_title() for cf in self.get_taxed_cashflows()]
        cashflows = [[cf[n].amount for cf in self.get_taxed_cashflows()] for n in periods]

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
        for n in range(self._periods + 1):
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
        for n in range(self._periods + 1):
            cfsum += sum(cf.amount for cf in self[n])
            if cfsum > 0:
                return n
        return -1

    def npw(self, i=None):
        if i is None and self._interest is None:
            raise ValueError(
                "No interest provided for npw calculations.\nDid you mean to use set_interest(i)?"
            )

        return sum([cf.to_pv(i or self._interest) for cf in self._cashflows]) or NullCashflow()

    def nfw(self, n, i=None):
        return self.npw().to_fv(i or self._interest, n)

    def bcr(self, i=None):
        if self._interest == None and i == None:
            raise ValueError(
                "No interest provided for bcr calculations. \nDid you mean to use set_interest(i)?"
            )

        pvb, pvc = 0, 0
        for n in range(self._periods + 1):
            for cf in self[n]:
                amt = cf.to_pv(i or self._interest).amount
                if amt > 0:
                    pvb += amt
                else:
                    pvc += amt

        if pvb == 0 or pvc == 0:
            return 0

        return abs(pvb / pvc)

    def eacf(self, d=None):
        d = parse_d(d or self._periods)
        return self.npw().to_av(self._interest, d)

    def irr(self, *, return_all=False, default=None):
        if not all(
            [  # Make sure we have both positive and negative net cashflows; else, IRR doesn't exist
                any([(sum(cfs) or NullCashflow()).amount > 0 for cfs in self[:]]),
                any([(sum(cfs) or NullCashflow()).amount < 0 for cfs in self[:]])
            ]
        ):
            return default

        def irr_fun(i):
            return self.npw(i[0]).amount

        irrs = fsolve(irr_fun, self._interest, factor=0.1)
        return irrs if return_all is True else irrs[0]

    def mirr(self, e_inv=None, e_fin=None):
        ncfs = self.get_ncfs()

        fvb = sum(
            [
                ncf.to_fv(e_fin or self._interest, self._periods)
                for ncf in ncfs
                if ncf.amount > 0
            ]
        ) or sp.Future(0, self._periods)
        pvc = sum(
            [ncf.to_pv(e_inv or self._interest) for ncf in ncfs if ncf.amount < 0]
        ) or sp.Present(0)

        return fsolve(lambda i: (fvb.to_pv(i) + pvc).amount, self._interest, factor=0.1)[
            0
        ]

