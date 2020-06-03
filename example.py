from PyEEA import Project
from PyEEA import SinglePaymentFactory as sp

my_project = Project(interest=0.12)

my_project                               \
    .add_cashflow(sp.Present(-1200))     \
    .add_cashflow( sp.Future( 100,  1))  \
    .add_cashflow( sp.Future( 200,  3))  \
    .add_cashflow( sp.Future( 1200, 5))

print("Net Present Worth of Project: $%.2f" % my_project.npw())