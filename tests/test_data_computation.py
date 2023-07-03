from pathlib import Path
import pickle
import matplotlib.pyplot as plt

from data_analysis.data_computation import *
import data_analysis.data_extraction as de
from data_analysis.measurement.newport_power_meter import NewportModel835PowerMeterMeasurements
from data_analysis.measurement.thorlabs_power_meter import ThorLabsPM100A_S120VC_PowerMeterMeasurement


def test_compute_powers_vs_mirror_angle():
    """Tests to see if the proper result is obtained when computing a result"""
    # First make a trial
    trial = de.extract_trial_info(
        Path("../Trials/GH13-12V (B) (Newer) (LEFT) (S) (1)"))
    # Compute the correct answer for the incident power at incident angle == 18
    # First get the data at this incident angle
    data = trial.data[trial.data[:, trial.incident_angle_column] == -18]
    mirror_angles = np.unique(data[:, trial.mirror_angle_column])
    trans_and_reflec_powers = np.zeros((1, 4))
    for mirror_angle in mirror_angles:
        replicates = data[data[:, trial.mirror_angle_column] == mirror_angle]
        transmitted_power = NewportModel835PowerMeterMeasurements(
            replicates[:, 2])
        reflected_power = ThorLabsPM100A_S120VC_PowerMeterMeasurement(
            replicates[:, 1], 637.8)
        incident_power = trial.beam_splitter.compute_incident_power(
            trial.polarization, NewportModel835PowerMeterMeasurements(transmitted_power.average()), ThorLabsPM100A_S120VC_PowerMeterMeasurement(reflected_power.average(), 637.8), trial.transmitted_background, trial.reflected_background)  # type: ignore
        element = np.column_stack(
            (mirror_angle, incident_power, transmitted_power.average(), reflected_power.average()))
        trans_and_reflec_powers = np.append(
            trans_and_reflec_powers, element, axis=0)
    trans_and_reflec_powers = trans_and_reflec_powers[1:]
    # now compute method to test
    powers = trial.compute_powers_vs_mirror_angle(np.array([18])).get(18)
    assert np.array_equal(powers, trans_and_reflec_powers)  # type: ignore
