# Cashflow Template

Snippet of a Python Cashflow object template:

``` Python
from .Cashflow import Cashflow

def MyCashflow(Cashflow):
    def __init__(self, amount, interest, other_param):
        super().__init__(amount, interest)
        # Other logic, e.g.
        self.foo = other_param

    def to_pv(self):
        pass

    def to_fv(self, n):
        pass

    def to_an(self, n):
        pass

    # Other methods....

```