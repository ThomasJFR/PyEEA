from copy import deepcopy
from collections.abc import Iterable

from ..valuators import npw, nfw, eacf, bcr, irr, mirr

class WhatIfAnalysis:
    def __init__(self, project):
        self._project = deepcopy(project)

    def analyse(self, cashflows, valuator=npw):
        if not isinstance(cashflows, Iterable):
            cashflows = [cashflows]
        self._project.add_cashflows(cashflows)

    def get_project():
        return self._project

    def get_dataframe():
        pass

    def get_chart():
        pass


class SensitivityAnalysis(WhatIfAnalysis):
    pass

class SimulationAnalysis(WhatIfAnalysis):
    pass


