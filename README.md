# PyEEA
<img align='right' src='./assets/logo.ico' alt=''/>

A Python3 library for engineering economic analysis.

``` Python
from PyEEA import Project, Present, Future, Annuity

msp = Project("My Sample Project", interest=0.12)
msp.add_cashflows([
    Present(-1000),
    Annuity(200, 5),
    Future(100, 6)
])
msp.show()
```
Core Features:
 * Cashflow models with built-in conversions to `Present`, `Future`, and `Annuity` types
 * Project object to enscapsulate and visualize Cashflows
 * Project valuation and analysis engines
 * Taxation and depreciation tools

## Installation

For now, the library is local. Install this module locally to *site-packages* or a directory of your choice.

## Documentation

Refer to the [PyEEA Wiki](https://github.com/ThomasJFR/PyEEA/wiki) for documentation. 

## Pronunciation

Proncounced ["Paella"](https://howdoyousaythatword.com/word/paella-spanish/)
