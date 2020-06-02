from PyPWA import Project
from PyPWA import SinglePaymentFactory as sp
# from PyPWA import UniformSeriesFactory as us

p1 = Project(interest=0.12)

i = 0.12
c = sp.Future(100, i, 4)
print("\nPresent Value for Future Cashflow of $100: $%d\n" % c.to_pv().amount)
print(c.to_fv(3))

