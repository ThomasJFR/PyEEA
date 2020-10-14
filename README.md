# PyEEA
<img align='right' src='./assets/logo.ico' alt=''/>

A Python3 library for engineering economic analysis.

``` Python
from PyEEA import Project, Present, Future, Annuity

msp = Project("My Sample Project", interest=0.12)
msp.add_cashflows((
    Present(-1000),
    Annuity(300, 5),
    Future(800, 6),
))
msp
# OUTPUT: Pandas DataFrame
#     Present 1 Annuity 2 Future 3
# 0  -$1,000.00     $0.00    $0.00
# 1       $0.00   $300.00    $0.00
# 2       $0.00   $300.00    $0.00
# 3       $0.00   $300.00    $0.00
# 4       $0.00   $300.00    $0.00
# 5       $0.00   $300.00    $0.00
# 6       $0.00     $0.00  $800.00

msp.npw()
# OUTPUT: Present
#  $486.74(P)

msp.show()
# OUTPUT: Matplotlib Plot
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
