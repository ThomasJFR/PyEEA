from PyEEA import Project
from PyEEA import SinglePaymentFactory as sp
from PyEEA import UniformSeriesFactory as us
from PyEEA import DepreciationHelper as dh
from PyEEA.output import write_excel, SpreadsheetFeature as ssfs
from matplotlib import pyplot as plt
print("CASHFLOW STUFF")
print("--------------")

depreciator = dh.DoubleDecliningBalance(0.20, 10, title="Big Boy", cashflows=[
    sp.Present(-100000),
], salvage=10000)

for i in range(12):
    print(depreciator[i])

p = Project(0.1)
p.add_cashflow(depreciator)
print(p.npw())
print("Now:", depreciator[0], p[0])

print("PROJECT STUFF")
print("-------------")
my_project = Project(interest=0.12)
my_project.add_cashflows([
    sp.Present(-1000,  title="Capital Costs"),
    us.Annuity(500, 5, title="Annual Benefits")
])
print(my_project.irr())

print("NPW Before: %s" % str(my_project.npw()))

from PyEEA import simulation_analysis, sensitivity_analysis
import pandas as pd
def sawtooth():
    from numpy.random import random
    return random() * 25
eacfs = simulation_analysis(my_project, {"Capital Costs": 100, "Annual Benefits": sawtooth}, valuator=my_project.eacf)
plt.hist([eacf.amount for eacf in eacfs])
plt.show()

#npw_sensitivities = sensitivity_analysis(my_project)
irr_sensitivities = sensitivity_analysis(my_project, [0.7, 0.85, 1, 1.15, 1.30], valuator=my_project.irr)
df = pd.DataFrame(
        #[[npw.amount for npw in npws] for npws in npw_sensitivities], 
        irr_sensitivities.values(),
        columns=["-30%", "-15%", "Actual", "+15%", "+30%"],
        index=irr_sensitivities.keys())
df.style.set_caption("Hello World")
print(df)

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
