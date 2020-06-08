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
                self.duration = cf.n
        elif isinstance(cf, sp.Annuity):
            if cf.d[1] > self.periods:
                self.duration = cf.d[1]

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
        match_period = lambda cf, n: any([isinstance(cf, sp.Present) and n == 0,
                                          isinstance(cf, sp.Future) and cf.n == n,
                                          isinstance(cf, us.Annuity) and cf.n in range(cf.d[0], cf.d[1] + 1)])
        ncfs = []
        for n in range(self.duration + 1):
            cfs = [cf for cf in self.cashflows if match_period(cf, n)]
            if len(cfs) == 0:
                ncfs.append(sp.Present(0) if n == 0 else sp.Future(0, n))
                continue
            
            ncf = sp.Present(0) if n == 0 else sp.Future(0, n)
            for cf in cfs:
                if isinstance(cf, sp.Present) or isinstance(cf, sp.Future):
                    ncf += cf
                elif isinstance(cf, us.Annuity):
                    ncf += cf.cf_at(n)
            ncfs.append(ncf)

        return ncfs

    def npw(self, i=None):
        if self.interest == None and i == None:
            raise ValueError('No interest provided for npw calculations.\
                              \nDid you mean to use set_interest(i)?')
        else:
            return sum([cf.to_pv(self.interest) for cf in self.cashflows])

    def eucf(self, n=None):
        if n == None:
            raise NotImplementedError
        return self.npw().to_av(self.interest, n)

    def irr(self):
        pass  # solve for NPW = 0

    def mirr(self):
        ncfs = self.get_ncfs()
        
        fvb = sum([ncf.to_fv(self.interest, self.duration) for ncf in ncfs if ncf.amount > 0]) or sp.Future(0, self.duration)
        pvc = sum([ncf.to_pv(self.interest) for ncf in ncfs if ncf.amount < 0]) or sp.Present(0)
        
        return fsolve(lambda i: (fvb.to_pv(i) + pvc).amount, self.interest)

    def describe():
        pass
