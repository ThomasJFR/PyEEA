from copy import deepcopy
from collections.abc import Iterable

class WhatIfAnalysis:
    def __init__(self, project):
        self._project = deepcopy(project)

    def get_project(self):
        self._project

    def analyse(self, cashflows, valuator):
        if not isinstance(cashflows, Iterable):
            cashflows = [cashflows]
        
        self._project.add_cashflows(cashflows)
        

    def to_dataframe():
        pass

    def to_chart():
        pass


class SensitivityAnalysis(WhatIfAnalysis):
    pass

class SimulationAnalysis(WhatIfAnalysis):
    pass


