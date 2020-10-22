import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.cm import get_cmap
from matplotlib.colors import Colormap
from ..utilities import Scales, parse_d, get_final_period
from ..cashflow import Cashflow
name = "tab20"
def_cmap = get_cmap(name)  # type: matplotlib.colors.ListedColormap

def generate_cashflow_diagram(cashflows, d=None, net=False, scale=None, color=None, title=None):
    # Parse Args
    cashflows = (cashflows,) if isinstance(cashflows, Cashflow) else cashflows
    d = parse_d(d or get_final_period(cashflows, finite=True) or 5)
    net = bool(net)
    color = (color.colors if isinstance(color, Colormap) else color) or def_cmap.colors
    if scale:
        scale = (
            scale if isinstance(scale, Scales)
            else Scales[scale.upper()])

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

    plotdata.plot(kind="bar", stacked="true", ax=ax, color=color)
    ax.set_title(title)
    ax.set_ylabel("Cashflows" + (f" [{scale.name.title()}]" if scale else ""))
    ax.set_xlabel("Period")
    ax.axhline()
            
    return fig, ax

