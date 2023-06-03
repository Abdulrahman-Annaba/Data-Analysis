from data_analysis.measurement.thorlabs_power_meter import *

VALID_MEASUREMENT = np.array([0.01])
"""Power measurement to test against many logical statements."""


def test_correct_measurement():
    """Tests to see if we can obtain the correct measurements from the stored measurements."""
    # In nanometers
    wavelength = 637.8
    thorlabs_measurements = ThorLabsPM100A_S120VC_PowerMeterMeasurement(
        VALID_MEASUREMENT, wavelength)
    assert np.array_equal(VALID_MEASUREMENT, thorlabs_measurements.values)


def test_correct_absolute_uncertainty():
    """Tests to see if we are computing the proper absolute uncertainty"""
    # In nanometers
    wavelength = 637.8
    thorlabs_measurements = ThorLabsPM100A_S120VC_PowerMeterMeasurement(
        VALID_MEASUREMENT, wavelength)
    correct_abs_uncertainty = VALID_MEASUREMENT * 0.03
    assert np.array_equal(
        thorlabs_measurements.abs_uncertainty(), correct_abs_uncertainty)
