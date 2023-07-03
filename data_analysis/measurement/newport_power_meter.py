"""A module to implement power meter measurements for the Newport Model 835 Power Meter"""
import numpy as np
from enum import Enum

from data_analysis.measurement.measurement_definitions import Measurements
from data_analysis.data_computation import NoAveragePossibleException


class NewportModel835PowerMeterRange(Enum):
    """A enumeration over the allowed measurement ranges for the Newport Model 835 Power Meter"""
    Twonanowatts = 1
    Twentynanowatts = 2
    Twohundrednanowatts = 3
    Twomilliwatts = 4
    Twentymilliwatts = 5
    Twohundredmilliwatts = 6


class InvalidMeasurement(Exception):
    """Raised when a provided measurement should not be possible on the respective power meter."""
    pass


# Defines the fullscale fractional uncertainties associated with each range
NEWPORT_MODEL_835_POWER_METER_FULLSCALE_UNCERTANTIES = {
    NewportModel835PowerMeterRange.Twonanowatts: 0.002,
    NewportModel835PowerMeterRange.Twentynanowatts: 0.0005,
    NewportModel835PowerMeterRange.Twohundrednanowatts: 0.0005,
    NewportModel835PowerMeterRange.Twomilliwatts: 0.0005,
    NewportModel835PowerMeterRange.Twentymilliwatts: 0.0005,
    NewportModel835PowerMeterRange.Twohundredmilliwatts: 0.0005
}

# Defines the fractional reading uncertainties associated with each range
NEWPORT_MODEL_835_POWER_METER_READING_UNCERTANTIES = {
    NewportModel835PowerMeterRange.Twonanowatts: 0.004,
    NewportModel835PowerMeterRange.Twentynanowatts: 0.004,
    NewportModel835PowerMeterRange.Twohundrednanowatts: 0.002,
    NewportModel835PowerMeterRange.Twomilliwatts: 0.0015,
    NewportModel835PowerMeterRange.Twentymilliwatts: 0.001,
    NewportModel835PowerMeterRange.Twohundredmilliwatts: 0.001
}


class NewportModel835PowerMeterMeasurements:
    """Represents a set of Newport Model 835 Power Meter measurements"""

    _BIN_AVERAGE_BINS = np.array([10**i for i in range(-10, 11, 1)])
    """Defines the boundary values for each bin in a histogram. Each value is separated by a power of 10"""

    def __init__(self, values: np.ndarray):
        """Create a set of Newport Model 835 Power Meter measurements."""
        self.value = values

    @property
    def values(self) -> np.ndarray:
        """Returns the contained measurements."""
        return self.value

    @values.setter
    def values(self, value):
        """Sets the contained measurements to the specified value"""
        self.value = value

    def abs_uncertainty(self) -> np.ndarray:
        """Computes the one-sided absolute uncertainties associated with the contained measurements."""
        # Make the simple scalar function map against an array, then pass the array of measurements to obtain the ranges
        ranges: np.ndarray = np.vectorize(self._get_range)(self.values)
        # For each range, obtain the associated fullscale fractional uncertainty.
        fullscale_frac_uncertainties: np.ndarray = np.vectorize(
            lambda range: NEWPORT_MODEL_835_POWER_METER_FULLSCALE_UNCERTANTIES.get(range))(ranges)
        # For each range, obtain the associated reading fractional uncertainty.
        reading_frac_uncertainties: np.ndarray = np.vectorize(
            lambda range: NEWPORT_MODEL_835_POWER_METER_READING_UNCERTANTIES.get(range))(ranges)
        # Finally, compute the absolute uncertainty.
        return self.values * (fullscale_frac_uncertainties + reading_frac_uncertainties)

    def average(self) -> float:
        """Computes the bin average of the provided data.

        Raises NoAveragePossibleException if an average was not possible"""
        # Map the power to the bin it resides in. Bins are specified via BIN_AVERAGE_BINS
        digits = np.digitize(self.values, self._BIN_AVERAGE_BINS)
        # Find the most frequent bin. This assumes there is only one most frequent bin.
        unique_bins, counts = np.unique(digits, return_counts=True)
        most_frequent_bin = unique_bins[np.argmax(counts)]
        # Get the most frequent bin powers
        most_frequent_powers = self.values[digits == most_frequent_bin]
        # If there are no most frequent powers, raise NoAveragePossibleException. Otherwise, return the average power
        if len(most_frequent_powers) == 0:
            raise NoAveragePossibleException
        return np.average(most_frequent_powers)  # type: ignore

    @staticmethod
    def _get_range(measurement_value: float) -> NewportModel835PowerMeterRange:
        """Given a power measurement, return the range that this measurement would be located"""
        # Check the value against each range and return the corresponding range enumeration.
        if measurement_value >= 0 and measurement_value <= 0.000000002:
            return NewportModel835PowerMeterRange.Twonanowatts
        elif measurement_value > 0.000000002 and measurement_value <= 0.000000020:
            return NewportModel835PowerMeterRange.Twentynanowatts
        elif measurement_value > 0.000000020 and measurement_value <= 0.000000200:
            return NewportModel835PowerMeterRange.Twohundrednanowatts
        elif measurement_value > 0.000000200 and measurement_value <= 0.002:
            return NewportModel835PowerMeterRange.Twomilliwatts
        elif measurement_value > 0.002 and measurement_value <= 0.020:
            return NewportModel835PowerMeterRange.Twentymilliwatts
        elif measurement_value > 0.020 and measurement_value <= 0.200:
            return NewportModel835PowerMeterRange.Twohundredmilliwatts
        else:
            # If the measurement value did not fit in any of the ranges above, it must be invalid and not allowed.
            raise InvalidMeasurement


# Register this class as an implementation of Measurements
Measurements.register(NewportModel835PowerMeterMeasurements)