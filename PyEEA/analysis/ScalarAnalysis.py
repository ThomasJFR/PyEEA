from copy import deepcopy
from typing import Sequence, Collection
from numbers import Number
from abc import ABC, abstractmethod

class ValueAnalysis(ABC):
    """ Defines a valuation analysis process

    Given a project, performs an analysis of value when its cashflows are 
    subjected to a stimulus. A default visualization can be shown to
    investigate the result further.

    Attributes:
        project: A project instance to be analyzed

    See Also:
        Project
    """
    def __init__(self, project):
        self._project = deepcopy(project)

    @abstractmethod
    def apply(self):
        """ Parses and stores parameters for analysis
        
        Receives a set of parameters and stores them internally. These
        parameters will generally be used only in the valuate function.
        """
        pass

    def valuate(self, valuator, **kwargs):
        """ Stimulates a project and returns a valuation of the result
        
        Modifies the cashflows of a project according to the parameters
        supplied to apply() and then performs a valuation.

        Args:
            valuator: The valuation technique to be used; can supply the acronym
                as a string, or a reference to the valuation function
            **kwargs: Additional keyword arguments to pass to the valuator function

        Returns:
            The result of the specified valuation

        See Also:
            valuators (module)

        """
        if callable(valuator):
            valuator = valuator.__name__
        valuator = valuator.lower()
        valuator_fun = getattr(self._project, valuator)
        return valuator_fun(**kwargs)        


    def show(self):
        """ Default behaviour for visualization of analysis

        Can be overwritten in subclasses who would benefit from an alternative
        implementation
        """
        return self._project.show()

    def get_project(self):
        return self._project

class WhatIfAnalysis(ValueAnalysis):
    def apply(self, *args):
        if isinstance(args[0], Sequence):
            cashflows = args[0]
        else:
            cashflows = args
        self._project.add_cashflows(cashflows)

class ScalarAnalysis(ValueAnalysis):
    """ Valuates a project with scaled cashflows
    
    Wrapper for performing simple scalar multiplication analysis of a project;
    given a mapping of strings and scalar values, the base amount of all cashflows
    with a particular tag are multiplied by the corresponding scalar. Then,
    a valuation is performed which reveals the effect of this change.
    """

    def apply(self, *args):
        """ Parses a mapping of strings and floats

        Parses a Mapping of string-float pairs (representing tags and scalar
        multipliers) and multiplies Cashflows by scalars if the tags match.

        Args:
            *args: A string and float or a 2d list or Mapping of string-float pairs

        Raises:
            TypeError: A single string was supplied as an argument
            ValueError: The length of *args was not 1 or 2
        """
        scalarmap=dict()
        if len(args) == 1:
            sequence = args[0]
            if isinstance(sequence, str):
                raise TypeError("Sequence cannot be str")
            elif isinstance(sequence, Sequence):
                scalarmap = {tag: scalar for tag, scalar in sequence}
            elif isinstance(sequence, dict):
                scalarmap = sequence
        elif len(args) == 2:
            scalarmap = {args[0]: args[1]}
        else:
            return ValueError("apply() only accepts 1 or 2 arguments")
        
        for tag in scalarmap:
            for cashflow in self._project[tag]:
                cashflow.amount *= scalarmap[tag]
    
class SensitivityAnalysis(ValueAnalysis):
    """ Scalar analysis applied across a sequence of scalars

    
    """
    def __init__(self, project):
        super().__init__(project)
        self._scalars = list()
        self._tags = list()

    def apply(self, *args):
        # Detect invalid arguments
        if len(args) == 1:
            pass
            #if all([])

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
        

