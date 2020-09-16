from copy import deepcopy
from typing import Sequence, Collection

class ScalarAnalysis:
    def __init__(self, project):
        self._project = deepcopy(project)

    def apply(self, *args):
        """
            apply("mytag", 0.10)
            apply(["mytag," 0.10])
            apply([("mytag, 0.10"), ("mytag2", 0.15)])
        """ 
        # ARGUMENT PARSING
        tag_scalars = dict()
        # case: apply("mytag", 0.10)
        if len(args) == 2: 
            tag, scalar = args
            tag, scalar = str(tag), float(scalar)
            tag_scalars[tag] = scalar
        elif len(args) == 1 and isinstance(args, Sequence):
            largs = args[0]
            if isinstance(largs[0], str):
                tag, scalar = largs
                tag, scalar = str(tag), float(scalar)
                tag_scalars[tag] = scalar
            elif isinstance(largs[0], Collection): # list tuple etc
                for tag, scalar in args_list:
                    tag_scalars[str(tag)] = float(scalar)
        else:
            raise TypeError("Only one or two arguments may be supplied!")

        # ANALYSIS
        # We now have a dict of str-float pairs that we can map
        # to cashflows.
        for tag in tag_scalars:
            for cashflow in self._project[tag]:
                cashflow.amount *= tag_scalars[tag]

    def get_project(self):
        return self._project

class SensitivityAnalysis(ScalarAnalysis):
    def __init__(self, project):
        super().__init__(project)

    def apply(self, *args):
        # Detect invalid arguments
        if len(args) == 0 or len(args) > 2:
            return TypeError("Only one or two arguments may be supplied!")
        
        # Argument parser
        tag_factors = dict()

        # case: apply("mytag", 0.10)
        if len(args) == 2:
            if isinstance(args[1], Collection):
                tag_factors[args[0]] = args[1]
        
        if isinstance(args, Collection):
            # case: apply(["mytag", 0.10])
            if isinstance(args[0], str): 
                args = (args,)
            # case: apply([("mytag1", 0.10), ("mytag2", 0.15), ...])
            if isinstance(args[0], Collection): 
                for tag, scalar in args:
                    tag_scalars[tag] = scalar
        

