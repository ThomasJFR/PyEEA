def sensitivity_analysis(project, factors, cf_tags=None, valuator=None):
    valuator = valuator or project.npw
    cf_tags = cf_tags or [cf.get_title() for cf in project.get_cashflows()]
    if not callable(valuator):
        return TypeError("Valuator must be a callable construct!")

    all_valuations = {}
    valuated_cashflows = set()  # Prevents repeats
    for tag in cf_tags:
        n_cashflows = len(project[tag])
        if n_cashflows == 0:
            continue

        for i in range(n_cashflows):
            # Make sure we don't repeat any valuations
            if project[tag][i].get_title() in valuated_cashflows:
                continue
            valuated_cashflows.update(project[tag][i].get_title())

            valuations = []
            for factor in factors:
                with project as p:

                    p[tag][i].amount *= factor
                    valuations.append(valuator())

            all_valuations[p[tag][i].get_title()] = valuations

    return all_valuations
