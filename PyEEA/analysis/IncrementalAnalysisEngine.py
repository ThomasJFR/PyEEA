from scipy.optimize import fsolve


def dirr_analysis(projects, marr):
    """
    Incremental IRR Analysis
    """
    # Sort from lowest to highest cost
    sorted_projects = iter(sorted(projects, key=lambda p: -p.npw().amount))

    # Phase 1: Find a defender
    defender = None
    try:
        while candidate := next(sorted_projects):
            if candidate.irr() > marr:
                defender = candidate
                break

        # Phase 2: Perform Incremental IRR Analysis
        while challenger := next(sorted_projects):
            inc = lambda i: challenger.npw(i) - defender.npw(i)
            dirr = fsolve(inc, challenger.interest)  # Not guaranteed to work!
            if dirr > marr:
                defender = challenger
    except StopIteration:
        return defender
