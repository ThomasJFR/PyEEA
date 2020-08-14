from PyEEA import Project
from PyEEA import SinglePaymentFactory as sp
from PyEEA import UniformSeriesFactory as us
from PyEEA import TaxationHelper as th, DepreciationHelper as dh

print("CASHFLOW STUFF")
print("--------------")

lumber = Project("Lumber Spotter", 0.22)
lumber.add_cashflows([
    dh.DecliningBalance(sp.Present(-80000, title="Capital"), 0.25, 10, first_claim=0.50,tags="CCA"),
    us.Annuity( 55000, 10, tags="CCA", title="Gross Income"),
    us.Annuity(-25000, 10, tags="CCA", title="Expenses"),
])

lumber.to_cashflowdiagram()
lumber.add_tax(th.Tax("CCA", 0.40))
print(lumber.to_dataframe())
print(lumber.npw())
print(lumber.eacf())
print(lumber.irr())
