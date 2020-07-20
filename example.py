from PyEEA import Project
from PyEEA import SinglePaymentFactory as sp
from PyEEA import UniformSeriesFactory as us
from PyEEA import DepreciationHelper as dh
from PyEEA.output import write_excel, SpreadsheetFeature as ssfs

print("CASHFLOW STUFF")
print("--------------")

depreciator = dh.DoubleDecliningBalance(0.20, 10, title="Big Boy", cashflows=[
    sp.Present(-100000),
], salvage=10000)

for i in range(12):
    print(depreciator[i])

print("PROJECT STUFF")
print("-------------")
my_project = Project(interest=0.12)
my_project                                                              \
    .add_cashflow(sp.Present( 5000,         title="Initial Payment"))   \
    .add_cashflow(us.Annuity( 250, [2,5],   title="Benefits"))          \
    .add_cashflow( sp.Future(-600,  2,      title="Maintenance 1"))     \
    .add_cashflow( sp.Future(-500,  3,      title="Maintenance 2"))     \
    .add_cashflow( sp.Future(-100, 5,       title="Maintenance 3"))     \
    .add_cashflow(us.Perpetuity(50, 2,      title="Lottery Win"))       \
    .add_cashflow(us.GeoPerpetuity(10, 0.1, title="Yearly Bonus"))

"""
print([[str(cf) for cf in p] for p in my_project[:]])
print("Net Present Worth:", my_project.npw())
print("Net Future Worth at n=5:", my_project.nfw(5))
print("Equivalent Uniform Cashflow of Project:", my_project.eacf(5))
print("Benefit-to-Cost Ratio:", my_project.bcr())
print("IRR:", my_project.irr())
print("MIRR:", my_project.mirr())
write_excel("test.xlsx", my_project, [ssfs.NPW, ssfs.CNPW])
"""
