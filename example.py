from PyEEA import Project
from PyEEA import SinglePaymentFactory as sp
from PyEEA import UniformSeriesFactory as us
from PyEEA.output import write_excel, SpreadsheetFeature as ssfs

print("CASHFLOW STUFF")
print("--------------")
gp = us.GeoPerpetuity(1200, 0.15, 1)
print(gp)
print(gp[0])
print([str(cf) for cf in gp[1, 5]])
print([str(cf) for cf in gp[1:3]])

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

print([[str(cf) for cf in p] for p in my_project[:]])
print("Net Present Worth:", my_project.npw())
print("Equivalent Uniform Cashflow of Project:", my_project.eacf(5))
print("Benefit-to-Cost Ratio:", my_project.bcr())
print("IRR:", my_project.irr())
print("MIRR:", my_project.mirr())
write_excel("test.xlsx", my_project, [ssfs.NPW, ssfs.CNPW])

""" QUIZ 
p = Project(interest=0.10)
p.add_cashflows([
    sp.Present(-1000),
    us.Annuity( 500, 5)
])
print(p.bcr())
"""
