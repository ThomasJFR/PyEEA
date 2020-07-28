from numpy.random import standard_normal
from numbers import Number

def simulation_analysis(project, sim_dict, iterations=250, valuator=None):
    """
    Purpose:
        Analyses the effects of uncertainty of a system by performing a Monte Carlo simulation.
    Args:
        project:    An instance of Project to perform the simulation on
        sim_dict:   A dict where the key is the name of the cashflow to simulate and the value 
                    is either a number defining the standard deviation for the cashflow, or a 
                    function defining some way to modify the cashflow by an amount
    """
    
    # Make every sim_fun value a callable, converting numbers to stdev functions
    for key in sim_dict:
        if isinstance(sim_dict[key], Number):
            stdev = sim_dict[key]
            def std_dist():
                return stdev * standard_normal()
            sim_dict[key] = std_dist
    
    valuator = valuator or project.npw
    if not callable(valuator):
        return TypeError("Valuator must be a callable construct!")

    # Perform the simulation
    valuations = []
    for _ in range(iterations):
        with project as p:
            for key in sim_dict:
                sim_fun = sim_dict[key]
                cf = p[key]
                cf.amount += sim_fun()
            valuations.append(valuator())

    return valuations

