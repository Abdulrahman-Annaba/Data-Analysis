"""Tests related to the Measurement implementation of the Newport Model 835 Power Meter"""
from data_analysis.measurement.newport_power_meter import *

VALID_SET_OF_DIFFERENT_MEASUREMENTS = np.array(
    [0.000000002, 0.000000001, 0, 0.000000005, 0.000000020, 0.000000200, 0.000000012, 0.002, 0.000005, 0.020, 0.010, 0.200, 0.100])
"""Multiple different power measurements to test against many logical statements."""

VALID_SET_OF_ABSOLUTE_UNCERTAINTIES = np.array([0.000000002*(0.002 + 0.004), 0.000000001*(0.002 + 0.004), 0, 0.000000005*(0.0005 + 0.004), 0.000000020*(
    0.0005 + 0.004), 0.000000200*(0.0005 + 0.002), 0.000000012*(0.0005 + 0.004), 0.002*(0.0005 + 0.0015), 0.000005*(0.0005 + 0.0015), 0.020*(0.0005 + 0.001), 0.010*(0.0005 + 0.001), 0.200*(0.0005 + 0.001), 0.100*(0.0005 + 0.001)])
"""Multiple different power measurements to test correct computation of absolute uncertainties associated with `VALID_SET_OF_DIFFERENT_MEASUREMENTS`"""


def test_correct_measurement():
    """Tests to see if we can obtain the correct measurements from the stored measurements."""
    newport_measurements = NewportModel835PowerMeterMeasurements(
        VALID_SET_OF_DIFFERENT_MEASUREMENTS)
    # Check if we can check our array
    assert np.array_equal(newport_measurements.values(),
                          VALID_SET_OF_DIFFERENT_MEASUREMENTS)


def test_correct_absolute_uncertainties():
    """Tests to see if we are computing the proper absolute uncertainties"""
    newport_measurements = NewportModel835PowerMeterMeasurements(
        VALID_SET_OF_DIFFERENT_MEASUREMENTS)
    # Check that the absolute uncertainty we compute is the same as the absolute uncertainty that we know is correct.
    assert np.array_equal(newport_measurements.abs_uncertainty(),
                          VALID_SET_OF_ABSOLUTE_UNCERTAINTIES)
