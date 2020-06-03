# Cashflow Template

Snippet of a Python Cashflow object template:

``` Python
from .Cashflow import Cashflow

def MyCashflow(Cashflow):
    def __init__(self, amount, other_param):
        super().__init__(amount)
        # Other logic, e.g.
        self.foo = other_param

    def to_pv(self, i):
        pass

    def to_fv(self, i, n):
        pass

    def to_an(self, i, n):
        pass

    # Other class methods....

```