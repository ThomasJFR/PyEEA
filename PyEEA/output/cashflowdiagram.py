import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.cm import get_cmap
from ..utilities import Scales, parse_d, get_final_period

name = "tab20"
cmap = get_cmap(name)  # type: matplotlib.colors.ListedColormap
tab20 = cmap.colors    # type: list


def generate_cashflow_diagram(cashflows, d=None, net=False, scale=None, title=None):
    # Parse Args
    d = parse_d(d or get_final_period(cashflows, finite=True) or 5)
    net = bool(net)
    if scale:
        scale = (
            scale if isinstance(scale, Scales) else
            Scales[scale.upper()])

    # Extract information
    periods   = list(range(d[0], d[1] + 1))
    titles    = [cashflow.get_title() for cashflow in cashflows] 
    cashflows = [
        [cashflow[n].amount for cashflow in cashflows]
        for n in periods
    ]

    # Format information
    if net:
        cashflows = [
            [sum(cashflows[n])] for n in periods
        ]
    if scale:
        cashflows = [
            [cashflow * scale.value for cashflow in cashflows[n]]
            for n in periods
        ]

    # Plot the Cashflow Diagram with matplotlib
    plotdata = pd.DataFrame(cashflows, index=periods, columns=titles)
    fig, ax = plt.subplots()

    plotdata.plot(kind="bar", stacked="true", ax=ax, color=tab20)
    ax.set_title(title)
    ax.set_ylabel("Cashflows" + (scale.name.lower() if scale else ""))
    ax.set_xlabel("Period")
    ax.axhline()
            
    return fig, ax

