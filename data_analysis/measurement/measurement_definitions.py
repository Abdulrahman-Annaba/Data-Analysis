"""Module containing definitions on how objects should interact with each other"""
from abc import ABC, abstractmethod
import numpy as np


class Measurements(ABC):
    """Defines an interface for measurements"""

    @property
    @abstractmethod
    def values(self) -> np.ndarray:
        """Defines a way to access a numpy array containing the actual measurement values"""
        pass

    @values.setter
    @abstractmethod
    def values(self, data: np.ndarray):
        """Defines a way to set a numpy array containing the actual measurement values"""
        pass

    @abstractmethod
    def abs_uncertainty(self) -> np.ndarray:
        """Computes the one-sided absolute uncertainty of the contained values"""
        pass

    @abstractmethod
    def average(self) -> float:
        """Computes the average of the contained data."""
        pass
