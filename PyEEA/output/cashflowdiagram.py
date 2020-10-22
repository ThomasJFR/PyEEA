import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.cm import get_cmap
<<<<<<< HEAD
from matplotlib.colors import Colormap
=======
from matplotlib.colors import ListedColormap
>>>>>>> f7493f901f026c371fd45803af549929fc7a5e1d
from ..utilities import Scales, parse_d, get_final_period
from ..cashflow import Cashflow
name = "tab20"
default_colormap = get_cmap(name)  # type: matplotlib.colors.ListedColormap

def generate_cashflow_diagram(
        cashflows, d=None, net=False, scale=None, color=None, title=None, **kwargs):
    """ Generates a barplot showing cashflows over time

    Given a set of cashflows, produces a stacked barplot with bars at each
    period. The height of each bar is set by the amount of cash produced
    by a cashflow at the specified period.

    Note that this function does not display the produced plot; call
    matplotlib.pyplot.show() to view the plot.

    Args:
        cashflows: A sequence of cashflows to plot
        d: Optional; A two-integer list whose elements represent the first
            and final periods to be plotted
        net: Optional; When true, only the net cashflows are shown, and the
            individual cashflow information is omitted.
        scale: Optional; The y-axis scale; must be a member or key of Scales
        kwargs: A list of keyword arguments to be passed to Dataframe.plot()
    
    Returns:
        A Figure and Axis for the plot
    """
    # Parse Args
    cashflows = (cashflows,) if isinstance(cashflows, Cashflow) else cashflows
    d = parse_d(d or get_final_period(cashflows, finite=True) or 5)
    net = bool(net)
    color = (color.colors if isinstance(color, Colormap) else color) or def_cmap.colors
    if color:
        color = color.colors if isinstance(color, ListedColormap) else color
    else:
        color = default_colormap.colors
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
        cashflows = [[sum(cashflows[n])] for n in periods]
    if scale:
        cashflows = [
            [cashflow * scale.value for cashflow in cashflows[n]]
            for n in periods
        ]

    # Plot the Cashflow Diagram with matplotlib
    plotdata = pd.DataFrame(cashflows, index=periods, columns=titles)
    fig, ax = plt.subplots()

    plotdata.plot(kind="bar", stacked="true", ax=ax, color=color, **kwargs)
    ax.set_title(title)
    ax.set_ylabel("Cashflows" + (f" [{scale.name.title()}]" if scale else ""))
    ax.set_xlabel("Period")
    ax.axhline()
            
    return fig, ax

