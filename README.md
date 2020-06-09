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

To view the cashflows occuring at each period (as an array of `Cashflow` instances), we use indeces and slices as follows:
``` Python
my_project[1]    # Gets the cashflows at period 1
my_project[2,5]  # Gets the cashflows at periods 2 and 5
my_project[:3]   # Gets the cashflows up to and including period 3
my_project[2:5]  # Gets the cashflows between periods 2 and 5, inclusive
my_project[::2]  # Gets the cashflows from every second period
```

### Cashflow Models

Several cashflow models are supported, as follows:

``` Python
from PyEEA import SinglePaymentFactory as sp
sp.Present( 1000)  # << Present:  $1000 >>
sp.Future( -1000, 3)  # << Future:  -$1000 @ n=3 >>

from PyEEA import UniformSeriesFactory as us
us.Annuity(       1000, 5)              # $1000('A', [0, 5])
us.Gradient(      1000, [4],     100)   # $1000('G', [0, 4], 100)
us.Geometric(     1000, [1, 10], 0.04)  # $1000('g', [1, 10], 4%)
us.Perpetuity(    100)			# $100('A', 'inf')
us.GeoPerpetuity( 100, 0.05)		# $100('g', 'inf', 5%)
```

### Project Valuation

Once a project has been defined with a variety of cashflows, we can valuate the project using a variety of valuation methods:

``` Python
my_project.ncfs()  # Net Cashflows for Every Period
my_project.npw()   # Net Present Worth
my_project.bcr()   # Benefit-to-Cost Ratio
my_project.eucf()  # Equivalent Uniform Cashflow
my_project.irr()   # Internal Rate of Return
my_project.mirr()  # Modified Internal Rate of Return
```

## Pronunciation

Proncounced ["Paella"](https://howdoyousaythatword.com/word/paella-spanish/)
