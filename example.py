from PyPWA import Project
from PyPWA import SinglePaymentFactory as sp
# from PyPWA import UniformSeriesFactory as us

p1 = Project()
i = 0.12

p1.add_cost(      sp.Present(1200, i))    \
    .add_revenue( sp.Future(100,   i, 1)) \
    .add_revenue( sp.Future(200,   i, 3)) \
    .add_revenue( sp.Future(1200,  i, 5))

print("Net Present Worth: $%.2f" % p1.npw())

