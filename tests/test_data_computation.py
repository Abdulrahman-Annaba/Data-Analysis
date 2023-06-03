from pathlib import Path
import pickle

from data_analysis.data_computation import *
import data_analysis.data_extraction as de


def test_compute_efficiency_vs_incident_angle():
    """Tests to see if the proper result is obtained when computing a result"""
    # First make the trial
    trial = de.extract_trial_info(
        Path("../Trials/GH13-12V (B) (Newer) (LEFT) (S) (1)"))
    # Now bring in correct result
    correct_file = open(
        "./tests/efficiency_vs_incident_angle_correct_output.pkl", "rb")
    correct_output = pickle.load(correct_file)
    correct_file.close()
    # Now compute output and check if they are the same
    output = trial.compute_efficiency_vs_incident_angle()
    assert np.array_equal(output, correct_output)


def test_compute_efficiency_vs_mirror_angle():
    """Tests to see if the proper result is obtained when computing a result"""
    # First make the trial
    trial = de.extract_trial_info(
        Path("../Trials/GH13-12V (B) (Newer) (LEFT) (S) (1)"))
    # Now bring in correct result.
    correct_file = open(
        "./tests/efficiency_vs_mirror_angle_correct_output.pkl", "rb")
    correct_output = pickle.load(correct_file)
    correct_file.close()
    # Default for all grating angles available in dataset
    output = trial.compute_efficiency_vs_mirror_angle()
    # check that we have dictionaries
    assert isinstance(output, dict)
    assert isinstance(correct_output, dict)
    # Check that the dictionary components are the same
    for ((k1, v1), (k2, v2)) in zip(output.items(), correct_output.items()):
        assert k1 == k2
        assert np.array_equal(v1, v2)


def test_compute_powers_vs_mirror_angle():
    """Tests to see if the proper result is obtained when computing a result"""
    # First make a trial
    trial = de.extract_trial_info(
        Path("../Trials/GH13-12V (B) (Newer) (LEFT) (S) (1)"))
    # Now save correct result
    correct_file = open(
        "./tests/power_vs_mirror_angle_correct_output.pkl", "rb")
    correct_output = pickle.load(correct_file)
    correct_file.close()
    output = trial.compute_powers_vs_mirror_angle()
    # check that we have dictionaries
    assert isinstance(output, dict)
    assert isinstance(correct_output, dict)
    # Check that the dictionary components are the same
    for ((k1, v1), (k2, v2)) in zip(output.items(), correct_output.items()):
        assert k1 == k2
        assert np.array_equal(v1, v2)
