from abc import ABC
from copy import deepcopy
from collections.abc import Iterable

from ..valuators import npw, nfw, eacf, eacp, bcr, irr, mirr


class WhatIf(ABC):
    def __init__(self, project):
        self._project = deepcopy(project)
    
class WhatIfAnalysis:
    def __init__(self, project):
        self._project = deepcopy(project)
        self._valuator

    def analyse(self, cashflows):
        if not isinstance(cashflows, Iterable):
            cashflows = [cashflows]
        self._project.add_cashflows(cashflows)

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
