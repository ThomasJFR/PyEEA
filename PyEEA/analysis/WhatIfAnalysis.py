from abc import ABC
from copy import deepcopy
from collections.abc import Collection

from ..valuators import npw, nfw, eacf, eacp, bcr, irr, mirr


class WhatIf(ABC):
    def __init__(self, project):
        self._project = deepcopy(project)
    
class WhatIfAnalysis:
    def __init__(self, project):
        self._project = deepcopy(project)

    def apply(self, cashflows):
        if not isinstance(cashflows, Collection):
            cashflows = [cashflows]
        self._project.add_cashflows(cashflows)

    def valuate(self):
        


    def get_project():
        return self._project

    def get_dataframe():
        pass

    def get_chart():
        pass

class ScalarAnalysis():


class SensitivityAnalysis(WhatIfAnalysis):
    pass


class SimulationAnalysis(WhatIfAnalysis):
    pass

