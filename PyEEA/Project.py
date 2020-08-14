from .cashflow import Cashflow, NullCashflow
from .cashflow import SinglePaymentFactory as sp
from .cashflow import UniformSeriesFactory as us
from .cashflow import DynamicSeriesFactory as ds

from .taxation import TaxationHelper as th, DepreciationHelper as dh

from .valuation import npw, nfw, eacf, epcf, bcr, irr, mirr

from .utilities import parse_d, parse_ns, get_final_period

from math import isinf

from matplotlib.cm import get_cmap
name = "tab20"
cmap = get_cmap(name)  # type: matplotlib.colors.ListedColormap
tab20 = cmap.colors  # type: list

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
        self._title = str(title)
        self._interest = float(interest)

        self._cashflows = list()
        self._depreciations = list()
        self._taxes = list()
        

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
                stop = (val.stop or self.get_final_period(finite=True)) + 1
                step = val.step or 1
                ns = range(start, stop, step)

            # TODO ADD SUPPORT FOR TAXATION
            def get_cashflows_for_period(n):
                def do_include_cashflow(cf):
                    return any([
                        isinstance(cf, sp.Future) and n == cf.n,
                        isinstance(cf, us.Annuity) and cf.d[0] < n <= cf.d[1],
                        isinstance(cf, us.Perpetuity) and n > cf.d0,
                        isinstance(cf, ds.Dynamic) and cf.d[0] < n <= cf.d[1],
                    ])
                return [cf for cf in self.get_cashflows() if do_include_cashflow(cf)]
            
            cashflows = [[cf[n] for cf in get_cashflows_for_period(n)] for n in ns]
            return cashflows[0] if len(cashflows) == 1 else cashflows

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

    def get_interest(self):
        return self._interest

    def get_final_period(self, finite=False): 
        nf = get_final_period(self.get_cashflows(), finite=finite)
        return nf

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

        return self  # Daisy Chaining!

    def add_depreciation(self, depreciation):
        if not isinstance(depreciation, dh.Depreciation):
            raise TypeError("Argument must be a child of Depreciation")
        
        self._depreciations.append(depreciation)
        self.add_cashflows(depreciation.cashflows)

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

        periods = list(range((n or self.get_final_period(finite=True) or 5) + 1))
        titles = [cf.get_title() for cf in self.get_taxed_cashflows()]
        cashflows = [[str(cf[n]).split('(')[0] for cf in self.get_taxed_cashflows()] for n in periods]
        
        return pd.DataFrame(cashflows, index=periods, columns=titles)

    def to_cashflowdiagram(self, n=None, size=None):
        import pandas as pd
        from matplotlib import pyplot as plt

        periods = list(range((n or self.get_final_period(finite=True) or 5) + 1))
        titles = [cf.get_title() for cf in self.get_taxed_cashflows()]
        cashflows = [[cf[n].amount for cf in self.get_taxed_cashflows()] for n in periods]

        plotdata = pd.DataFrame(cashflows, index=periods, columns=titles)
        ax = plotdata.plot(kind="bar", stacked="true", color=tab20)
        ax.set_title(self.get_title())
        ax.set_ylabel("USD")
        ax.set_xlabel("Period")
        ax.axhline()

        if size:
            fig = plt.gcf()
            fig.set_size_inches(size)

    #################################
    ### PROJECT VALUATION HELPERS
    ###

    def npw(self, i=None, after_tax=True):
        i = i if i is not None else self.get_interest()
        if i is None:
            raise ValueError(
                "No interest provided for npw calculations."
                "Did you mean to use set_interest(i)?"
            )
        cashflows = self.get_taxed_cashflows() if after_tax else self.get_cashflows()
        return npw(cashflows, i)

    def nfw(self, n, i=None, after_tax=True):
        i = i if i is not None else self.get_interest()
        if i is None:
            raise ValueError(
                "No interest provided for nfw calculations."
                "Did you mean to use set_interest(i)?"
            )
        cashflows = self.get_taxed_cashflows() if after_tax else self.get_cashflows()
        return nfw(cashflows, i, n)

    def eacf(self, d=None, i=None, after_tax=True):
        d = parse_d(d if d is not None else self.get_final_period())
        
        if isinf(d[1]):
            return self.epcf(d[0], i, after_tax)
        
        i = i if i is not None else self.get_interest()
        if i is None:
            raise ValueError(
                "No interest provided for eacf calculations."
                "Did you mean to use set_interest(i)?"
            )
        cashflows = self.get_taxed_cashflows() if after_tax else self.get_cashflows()
        return eacf(cashflows, i, d)

    def epcf(self, d0=0, i=None, after_tax=True):
        i = i if i is not None else self.get_interest()
        if i is None:
            raise ValueError(
                "No interest provided for eacf calculations."
                "Did you mean to use set_interest(i)?"
            )
        cashflows = self.get_taxed_cashflows() if after_tax else self.get_cashflows()
        return epcf(cashflows, i, d0)

    def bcr(self, after_tax=True):
        cashflows = self.get_taxed_cashflows() if after_tax else self.get_cashflows()
        return bcr(cashflows)

    def irr(self, i0=None, after_tax=True):
        i0 = i0 if i0 is not None else self.get_interest()
        if i0 is None:
            raise ValueError(
                "No initial interest guess provided for irr calculations."
                "Did you mean to use set_interest(i)?"
            )

        cashflows = self.get_taxed_cashflows() if after_tax else self.get_cashflows()
        return irr(cashflows, i0)

    def mirr(self, e_inv=None, e_fin=None, after_tax=True):
        e_inv = e_inv if e_inv is not None else self.get_interest()
        e_fin = e_fin if e_fin is not None else self.get_interest()
        cashflows = self.get_taxed_cashflows() if after_tax else self.get_cashflows()
        return mirr(cashflows, e_inv, e_fin)

