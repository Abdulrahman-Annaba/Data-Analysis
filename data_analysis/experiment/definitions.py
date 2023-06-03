"""A module which contains some definitions in our experiment."""
from enum import Enum


class PowerMeterLabel(Enum):
    """Defines the allowed power meter label types"""
    A = 1
    B = 2


class PolarizationState(Enum):
    """Defines the allowed polarization states"""
    Horizontal = 1
    Vertical = 2
