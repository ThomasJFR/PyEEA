# PyEEA - A Python Engineering Economics Analysis Library
<img align='right' src='./assets/logo.ico' alt=''/>

A Python3 library for performing engineering economics analysis. Styled using [Black](https://github.com/psf/black)

Developed by Thomas Richmond and MArkos Frazzer.

## Installation

## Documentation

### Project Modelling

The intent of this library is to provide a clear illustration of cashflows within a project. 
The library uses daisy-chaining syntax to accomplish this in a line-by-line fashion,
similar to a typical spreadsheet.

For example, a simple project may have cashflows that look like this


``` Python
from PyEEA import Project
from PyEEA import SinglePaymentFactory as sp

my_project = Project(interest=0.12)

my_project                               \
    .add_cashflow(sp.Present(-1200))     \
    .add_cashflow( sp.Future( 100,  1))  \
    .add_cashflow( sp.Future( 200,  3))  \
    .add_cashflow( sp.Future( 1200, 5))

print("Net Present Worth of Project: $%.2f" % my_project.npw())
# Output: Net Present Worth of Project: $-287.45
```

An iterable syntax is also supported when supplying cashflows to a project
``` Python
my_project.add_cashflows([
    sp.Present(-1200),
     sp.Future( 100, 1),
     sp.Future( 300, 3),
     sp.Future( 1200, 5)
])
```

### Cashflow Models

Several cashflow models are supported, as follows:

``` Python
from PyEEA import SinglePaymentFactory as sp
sp.Present( 1000)  # << Present:  $1000 >>
sp.Future( -1000, 3)  # << Future:  -$1000 @ n=3 >>

from PyEEA import UniformSeriesFactory as us
us.Annuity(1000, [1, 10])  # << Annuity: $1000 for d=[1, 10] >>
us.Gradient(1000, [5, 10], 100) # << Gradient: $1000 with G= $100 for d=[5, 10]>>

# TODO:
us.Geometric(...)
us.Perpetuity(...)
us.GeoPerpetuity(...)
```

## Pronunciation

Proncounced ["Paella"](https://howdoyousaythatword.com/word/paella-spanish/)
