from copy import deepcopy
from collections.abc import Collection

from ..valuators import npw, nfw, eacf, eacp, bcr, irr, mirr


class WhatIfAnalysis:
    def __init__(self, project):
        self._project = deepcopy(project)

    def apply(self, cashflows):
        if not isinstance(cashflows, Collection):
            cashflows = [cashflows]
        self._project.add_cashflows(cashflows)
        return self._project

    def valuate(self):
        


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

