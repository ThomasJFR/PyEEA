# __init__.py
from .Project import Project

from .cashflow import Cashflow, NullCashflow

from .cashflow import SinglePaymentFactory
from .cashflow import UniformSeriesFactory
from .cashflow import ForecastModelFactory
from .cashflow import DynamicSeriesFactory

from .cashflow import (
    Present,
    Future,
    Annuity,
    Gradient,
    Geometric,
    Perpetuity,
    GeoPerpetuity,
    LearningCurve,
    Dynamic,
)

from .taxation import DepreciationHelper
from .taxation import TaxationHelper

from .analysis import (
    ScalarAnalysis,
    WhatIfAnalysis,
    SensitivityAnalysis,
    simulation_analysis,
    sensitivity_analysis
)

from .valuation import (
    npw,
    nfw,
    eacf,
    epcf,
    bcr,
    irr,
    mirr,
)

from .output import write_excel

from .utilities import Scales

__version__ = "0-A2"
__author__ = "Thomas Richmond"
