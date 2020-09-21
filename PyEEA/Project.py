from .cashflow import Cashflow, NullCashflow
from .cashflow import SinglePaymentFactory as sp
from .cashflow import UniformSeriesFactory as us
from .cashflow import DynamicSeriesFactory as ds

from .taxation import TaxationHelper as th, DepreciationHelper as dh

from .valuation import npw, nfw, eacf, epcf, bcr, irr, mirr

from .output import generate_cashflow_diagram

from .utilities import Scales, parse_d, parse_ns, get_final_period

from math import isinf

class Project:
    """ Contains many cashflows and shortcuts for analysis

    Projects contain cashflows and related constructs. (e.g. Tax
    schemes and Depreciating assets) Properties such as interest are 
    kept constant across all cashflows. The aggregate cashflows can
    be easily visualized, manipulated and analyzed to glean information
    about the emergent nature of the cashflows.

    See Also:
        Cashflow
        Depreciation
        Tax
    """

    def __init__(self, title=None, interest=0):
        """ Creates a project containing no cashflows or related constructs

        Args:
            title: Optional; A human-readable summary of the project
            interest: Optional; An interest rate to be applied across all 
                project cashflows and related constructs
        """
        self._title = str(title)
        self._interest = float(interest)

        self._cashflows = list()
        self._depreciations = list()
        self._taxes = list()

    def __repr__(self):
        """ Prints table of Cashflows vs periods """
        return self.to_dataframe().to_string()

    def __getitem__(self, val):
        """ Retrieves cashflows by tags or periods
        
        Proxy for...
        """
        # OPTION 1: Index by tags
        if type(val) is str:
            matches = self.get_cashflows(tags=val)
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

            cashflows = [
                    [
                        cashflow[n] 
                        for cashflow in self.get_cashflows()
                        if not isinstance(cashflow[n], NullCashflow)
                    ]
                    for n in ns
                ]
            return cashflows[0] if len(cashflows) == 1 else cashflows

    def set_title(self, title):
        self._title = title

    def get_title(self):
        return self._title or "Project with {} cashflows".format(
            len(self.get_cashflows())
        )

    def set_interest(self, interest):
        self._interest = interest

    def get_interest(self):
        return self._interest

    def get_final_period(self, finite=False):
        """ Returns the highest period in which Cashflows are still active

        Args:
            finite: If true, the method can return infinity if the project
                contains instances of Perpetuity
        """
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

    def get_cashflows(self, tags=None):
        if not tags:
            return self._cashflows
        
        if type(tags) is str:
            tags = [tags]
        
        cashflows = [
            [cashflow for cashflow in self._cashflows if tag in cashflow.tags]
            for tag in tags
        ]
        return cashflows[0] if len(cashflows) == 1 else cashflows

    def get_depreciations(self, tags=None):
        if not tags:
            return self._depreciations

        
        if type(tags) is str:
            tags = [tags]
        return [depreciation for depreciation in self._depreciations for tag in tags if tag in depreciation.tags]

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

    def get_taxflows(self, tags=None):
        return [
            tax.generate_cashflow(self.get_cashflows(tags=tags), self.get_depreciations(tags=tags))
            for tax in self.get_taxes()
        ]

    def get_taxed_cashflows(self, tags=None):
        return self.get_cashflows(tags=tags) + self.get_taxflows(tags=tags)

    def to_dataframe(self, to_period=None, net=False):
        import pandas as pd
        to_period = int(to_period or self.get_final_period(finite=True) or 5)
        periods = list(range(to_period + 1))
        titles = [cf.get_title() for cf in self.get_taxed_cashflows()]
        cashflows = [[cf[n] for cf in self.get_taxed_cashflows()] for n in periods]
        
        if net:
            titles=["Net Cashflows"]
            cashflows = [[sum(cashflows[n])] for n in periods]
       
        str_cashflows = [
            [str(cashflow).split(" ")[-1] for cashflow in cashflows[n]]
            for n in periods
        ]
        

        return pd.DataFrame(str_cashflows, index=periods, columns=titles)

    def to_cashflowdiagram(self, n=None, net=False, scale=None, size=None):
        fig, ax = generate_cashflow_diagram(
                self.get_taxed_cashflows(),
                n,
                net,
                scale,
                title=self.get_title())
        if size:
            fig.set_size_inches(size)
        return fig, ax

    def show(self, n=None, net=False, scale=None, size=None):
        from matplotlib import pyplot as plt
        self.to_cashflowdiagram(n, net, scale, size)
        plt.show()

    ## PROJECT VALUATION HELPERS

    def npw(self, i=None, after_tax=True, tags=None):
        i = i if i is not None else self.get_interest()
        if i is None:
            raise ValueError(
                "No interest provided for npw calculations."
                "Did you mean to use set_interest(i)?"
            )
        cashflows = self.get_taxed_cashflows(tags=tags) if after_tax else self.get_cashflows(tags=tags)
        return npw(cashflows, i)

    def nfw(self, n, i=None, after_tax=True, tags=None):
        i = i if i is not None else self.get_interest()
        if i is None:
            raise ValueError(
                "No interest provided for nfw calculations."
                "Did you mean to use set_interest(i)?"
            )
        cashflows = self.get_taxed_cashflows(tags=tags) if after_tax else self.get_cashflows(tags=tags)
        return nfw(cashflows, i, n)

    def eacf(self, d=None, i=None, after_tax=True, tags=None):
        d = parse_d(d if d is not None else self.get_final_period())

        if isinf(d[1]):
            return self.epcf(d[0], i, after_tax, tags=tags)

        i = i if i is not None else self.get_interest()
        if i is None:
            raise ValueError(
                "No interest provided for eacf calculations."
                "Did you mean to use set_interest(i)?"
            )
        cashflows = self.get_taxed_cashflows(tags=tags) if after_tax else self.get_cashflows(tags=tags)
        return eacf(cashflows, i, d)

    def epcf(self, d0=0, i=None, after_tax=True, tags=None):
        i = i if i is not None else self.get_interest()
        if i is None:
            raise ValueError(
                "No interest provided for eacf calculations."
                "Did you mean to use set_interest(i)?"
            )
        cashflows = self.get_taxed_cashflows(tags=tags) if after_tax else self.get_cashflows(tags=tags)
        return epcf(cashflows, i, d0)

    def bcr(self, after_tax=True, tags=None):
        cashflows = self.get_taxed_cashflows(tags=tags) if after_tax else self.get_cashflows(tags=tags)
        return bcr(cashflows)

    def irr(self, i0=None, after_tax=True, tags=None):
        i0 = i0 if i0 is not None else self.get_interest()
        if i0 is None:
            raise ValueError(
                "No initial interest guess provided for irr calculations."
                "Did you mean to use set_interest(i)?"
            )

        cashflows = self.get_taxed_cashflows(tags=tags) if after_tax else self.get_cashflows(tags=tags)
        return irr(cashflows, i0)

    def mirr(self, e_inv=None, e_fin=None, after_tax=True, tags=None):
        e_inv = e_inv if e_inv is not None else self.get_interest()
        e_fin = e_fin if e_fin is not None else e_inv
        cashflows = self.get_taxed_cashflows(tags=tags) if after_tax else self.get_cashflows(tags=tags)
        return mirr(cashflows, e_inv, e_fin)

