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

        self.revenues = []
        self.costs = []

    def __add__(self, them):
        agg = Project()
        for r1 in self.revenues:
            agg.add_revenue(r1)
        for r2 in them.revenues:
            agg.add_revenue(r2)
        for c1 in self.costs:
            agg.add_cost(c1)
        for c2 in them.costs:
            agg.add_cost(c2)

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

    def add_revenue(self, revenue):
        self.revenues.append(revenue)
        return self  # Daisy Chaining!

    def add_cost(self, cost):
        self.costs.append(cost)
        return self  # Daisy Chaining!

    def npw(self):
        npw = 0
        npw += sum([r.to_pv(self.interest).amount for r in self.revenues])
        npw -= sum([c.to_pv(self.interest).amount for c in self.costs])
        return npw

    def describe():
        pass
