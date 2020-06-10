from scipy.optimize import fsolve


def dirr_analysis(projects, marr):
    """
    Incremental IRR Analysis
    """
    # Sort from lowest to highest cost
    sorted_projects = iter(sorted(projects, key=lambda p: -p.npw().amount))

    # Phase 1: Find a defender
    while defender := next(sorted_projects):
        if defender.irr() > marr:
            break
    else:
        return None  # Yikes - no project is worth doing!

    # Phase 2: Perform Incremental IRR Analysis
    while challenger := next(sorted_projects):
        inc = lambda i: challenger.npw(i) - defender.npw(i)
        dirr = fsolve(inc, challenger.interest)  # Not guaranteed to work!
        if dirr > marr:
            defender = challenger
    return challenger
