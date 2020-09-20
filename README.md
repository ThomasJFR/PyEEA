# PyEEA - A Python Engineering Economics Analysis Library
<img align='right' src='./assets/logo.ico' alt=''/>

A Python3 library for performing engineering economics analysis.

``` Python
from PyEEA import Project, Present, Future, Annuity

msp = Project("My Sample Project", 0.12)
msp.add_cashflows([
    Present(-1000),
    Annuity(200, 5),
    Future(100, 6)
])
msp.show()
```


## Features

#### Define Projects using Cashflows
``` Python
from PyEEA import Project
from PyEEA import SinglePaymentFactory as sp
from PyEEA import UniformSeriesFactory as us

project = Project("Solar Plant Expansion Project", interest=0.10)

# Model projects using cashflow models
project.add_cashflow(sp.Present(-2500,  title="Raw Materials Purchase"))

# Add multiple cashflows at once!
project.add_cashflows([
    us.Annuity(-200, 5, title="Annual Pamphlet Costs")
    sp.Future(1000,  5, title="Sold Business Renevue")
])
```

#### Taxation and Tax Shields

``` Python
from PyEEA import DepreciationHelper as dh

capital_expenses = [
    sp.Present(-50000, title="High-Cost Tool"),
    sp.Present(-1600,  title="Installation Fees")
]

# Depreciate using a declining balance model over five years at 20% with a salvage value of $100
project.add_cashflows([
    dh.DecliningBalance(capital_expenses, 0.20, 5, salvage=100,
                        title="Asset Purchase and Setup", tags="VAT")
])

# Add 25% VAT tax to project
from PyEEA import TaxationHelper as th

project.add_tax(th.Tax("VAT", 0.25, title="Value-Added Tax"))
```

#### Visualize & Export Projects

``` Python
# Visualize our projects
project.to_dataframe()  # Using pandas
project.to_cashflowdiagram()  # Using matplotlib

# Export our project as an Excel file
from PyEEA.output import write_excel, SpreadsheetFeature as ssft
write_excel("SPEP_Finances.xlsx", spep,
            features=[ssft.NPW, ssft.CNPW])
```

#### Perform Valuation of Projects

``` Python
project.npw()   # Net Present Worth
project.nfw()   # Net Future Worth
project.bcr()   # Benefit-to-Cost Ratio
project.irr()   # Internal Rate of Return
project.mirr()  # Modified IRR
```

#### Perform Project Analysis

``` Python
# Sensativity Analysis
from PyEEA import sensativity_analysis

sens_factors = [0.70, 0.85, 1.00, 1.15, 1.30]
npws = sensitivity_analysis(project, sens_factors)
irrs = sensitivity_analysis(project, sens_factors, valuator=project.irr)

# Simulation Analysis
from PyEEA import simulation_analysis

sim_eacfs = simulation_analysis(project, {
        "Annual Pamphlet Costs": 0.10
    }, valuator=project.eacf)
```

## Installation

For now, the library is local. Install this module locally to *site-packages* or a directory of your choice.

## Documentation

Refer to the [PyEEA Wiki](https://github.com/ThomasJFR/PyEEA/wiki) for documentation. 

## Pronunciation

Proncounced ["Paella"](https://howdoyousaythatword.com/word/paella-spanish/)
