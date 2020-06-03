# PyEEA  <img align='right' src='./assets/logo.ico' alt=''/>

A Python3 library for performing engineering economics analysis. Styled using [Black](https://github.com/psf/black)

Developed by Thomas Richmond and MArkos Frazzer.

## Installation

## Documentation

The intent of this library is to provide a clear illustration of cashflows within a project. 
The library uses daisy-chaining syntax to accomplish this in a line-by-line fashion,
similar to a typical spreadsheet.

For example, a simple project may have cashflows that look like this


``` Python
from PyEEA import Project
from PyEEA import SinglePaymentFactory as sp

my_project = Project
my_project \
    .add_cost(    sp.Present(1200, i))    \
    .add_revenue( sp.Future(100,   i, 1)) \
    .add_revenue( sp.Future(200,   i, 3)) \
    .add_revenue( sp.Future(1200,  i, 5))
print("Net Present Worth of Project: $%.2f" % my_project.npw())
# Output: Net Present Worth of Project: $-287.45


## Pronunciation

Proncounced ["Paella"](https://howdoyousaythatword.com/word/paella-spanish/)
