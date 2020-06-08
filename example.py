from PyEEA import Project
from PyEEA import SinglePaymentFactory as sp

my_project = Project(interest=0.12)

my_project                                \
    .add_cashflow( sp.Future(-1000,  1))  \
    .add_cashflow( sp.Future(-600,  2))   \
    .add_cashflow( sp.Future(-500,  3))   \
    .add_cashflow( sp.Future(-100, 5))    \
    .add_cashflow( sp.Future( 5000, 5))

print("Equivalent Uniform Cashflow of Project:", my_project.eucf(1))
print("IRR:", my_project.irr())
print("MIRR:", my_project.mirr())
