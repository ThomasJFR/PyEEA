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

    def __init__(self, name="generator", interest=0.12):
        self.name = name
        self.interest = interest

        self.cashflows = []

    def __add__(self, them):
        agg = Project()
        for cf1 in self.cashflows:
            agg.add_cashflow(cf1)
        for cf2 in them.cashflows:
            agg.add_cashflow(cf2)
        
        return agg  # The aggregation of Projects

    def __lt__(self, them):
        return self.npw() < them.npw()

    def __le__(self, them):
        return self.npw() <= them.npw()

    def __gt__(self, them):
        return self.npw() > them.npw()

    def __ge__(self, them):
        return self.npw() >= them.npw()

    def set_name(self, name):
        self.name = name

    def set_interest(self, interest):
        self.interest = interest

    def add_cashflow(self, cf):
        self.cashflows.append(cf)
        return self  # Daisy Chaining!

    def revenues(self):
        return [cf for cf in self.cashflows if cf.amount > 0]

    def costs(self):
        return [cf for cf in self.cashflows if cf.amount < 0]

    def npw(self):
        return sum([cf.to_pv(self.interest).amount for cf in self.cashflows])

    def describe():
        pass
