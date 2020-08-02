
def sensitivity_analysis(project, factors, cf_titles=None, valuator=None):
    valuator = valuator or project.npw
    cf_titles = cf_titles or [cf.get_title() for cf in project.cashflows]
    if not callable(valuator):
        return TypeError("Valuator must be a callable construct!")

    all_valuations = {}
    for title in cf_titles:
        valuations = []
        for factor in factors:
            with project as p:
                p[title].amount *= factor
                valuations.append(valuator())
    
        all_valuations[title] = valuations
    

    return all_valuations

