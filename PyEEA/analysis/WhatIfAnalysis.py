from copy import deepcopy
from collections.abc import Iterable

from ..valuators import npw, nfw, eacf, eacp, bcr, irr, mirr


class WhatIfAnalysis:
    def __init__(self, project):
        self._project = deepcopy(project)
        self._valuator

    def analyse(self, cashflows):
        if not isinstance(cashflows, Iterable):
            cashflows = [cashflows]
        self._project.add_cashflows(cashflows)
        return self._project

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
