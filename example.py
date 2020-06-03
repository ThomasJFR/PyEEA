from PyEEA import Project
from PyEEA import SinglePaymentFactory as sp
# from PyEEA import UniformSeriesFactory as us

my_project = Project(interest=0.12)

my_project                            \
    .add_cost(   sp.Present(1200))    \
    .add_revenue( sp.Future(100, 1))  \
    .add_revenue( sp.Future(200, 3))  \
    .add_revenue( sp.Future(1200, 5))

print("Net Present Worth: $%.2f" % my_project.npw())

