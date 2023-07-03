"""A module to implement power meter measurements for the ThorLabs PM100A S120VC Power Meter and Sensor combination"""
import numpy as np
from enum import Enum
from data_analysis.measurement.measurement_definitions import Measurements
from data_analysis.data_computation import NoAveragePossibleException


class InvalidMeasurementWavelength(Exception):
    """Raised when a measurement is taken at an invalid wavelength for the power meter."""


class ThorlabsPm100aS120vcUncertaintyWavelengthRange(Enum):
    """Describes the possible wavelength ranges for determining the uncertainty in measurement"""
    Range440to980nm = 1
    Range280to439nm = 2
    Range200to279nm = 3
    Range981to1100nm = 4


THORLABS_PM100A_S120VC_WAVELENGTH_UNCERTAINTIES = {
    ThorlabsPm100aS120vcUncertaintyWavelengthRange.Range440to980nm: 0.03,
    ThorlabsPm100aS120vcUncertaintyWavelengthRange.Range280to439nm: 0.05,
    ThorlabsPm100aS120vcUncertaintyWavelengthRange.Range200to279nm: 0.07,
    ThorlabsPm100aS120vcUncertaintyWavelengthRange.Range981to1100nm: 0.07
}
"""Define the mapping of wavelength ranges to their corresponding fractional uncertainties."""


class ThorLabsPM100A_S120VC_PowerMeterMeasurement:
    """Define a set of ThorLabs PM100A S120VC power meter measurements"""
    _AVERAGE_MULTIPLIER = 5
    """The multiplicative factor to use when computing a sequenced average"""

    def __init__(self, values: np.ndarray, at_wavelength: float):
        """Creates a set of ThorLabs PM100A S120VC power meter measurements at the specified wavelength `at_wavelength` measured in nanometers"""
        self.value = values
        self.wavelength = at_wavelength
        self._frac_uncertainty = self._get_frac_uncertainty(at_wavelength)

    @staticmethod
    def _get_frac_uncertainty(wavelength: float) -> float:
        """Private method to determine the fractional uncertainty associated with the given wavelength."""
        if wavelength >= 200 and wavelength <= 279:
            return THORLABS_PM100A_S120VC_WAVELENGTH_UNCERTAINTIES[ThorlabsPm100aS120vcUncertaintyWavelengthRange.Range200to279nm]
        elif wavelength > 279 and wavelength <= 439:
            return THORLABS_PM100A_S120VC_WAVELENGTH_UNCERTAINTIES[ThorlabsPm100aS120vcUncertaintyWavelengthRange.Range280to439nm]
        elif wavelength > 439 and wavelength <= 980:
            return THORLABS_PM100A_S120VC_WAVELENGTH_UNCERTAINTIES[ThorlabsPm100aS120vcUncertaintyWavelengthRange.Range440to980nm]
        elif wavelength > 980 and wavelength <= 1100:
            return THORLABS_PM100A_S120VC_WAVELENGTH_UNCERTAINTIES[ThorlabsPm100aS120vcUncertaintyWavelengthRange.Range981to1100nm]
        else:
            raise InvalidMeasurementWavelength

    @property
    def values(self) -> np.ndarray:
        """Returns the measurement values"""
        return self.value

    @values.setter
    def values(self, value):
        self.value = value

    def abs_uncertainty(self) -> np.ndarray:
        """Computes the one-sided absolute uncertainties associated with the contained measurements."""
        return self._frac_uncertainty * self.values

    def average(self) -> float:
        """Private method to compute the average power. If the power is bad even after doing the succeeding averages, then a custom exception is raised (NoAveragePossibleException)."""
        # Compute the first average power
        first_average = np.average(self.values, axis=0)
        # Select power values that are less than 5 times the first average
        power = self.values[self.values <
                            first_average*self._AVERAGE_MULTIPLIER]
        # Select power values that are greater than 1/5 the first average
        power = power[power > first_average*1/self._AVERAGE_MULTIPLIER]
        # If the last conditional slice resulted in 0 power readings that were close to the first average
        if len(power) == 0:
            raise NoAveragePossibleException
        # Return the final average. This assumes that the previous steps removed the extremal values
        return np.average(power, axis=0)


# Register this class as an implementation of Measurements
Measurements.register(ThorLabsPM100A_S120VC_PowerMeterMeasurement)