
def sensitivity_analysis(project, factors, valuator=None):
    valuator = valuator or project.npw
    if not callable(valuator):
        return TypeError("Valuator must be a callable construct!")

    all_valuations = {}
    titles = [cf.get_title() for cf in project.cashflows]
    for title in titles:
        valuations = []
        for factor in factors:
            with project as p:
                p[title].amount *= factor
                valuations.append(valuator())
    
        all_valuations[title] = valuations
    

    return all_valuations

