from data_analysis.experiment.definitions import *


def test_polarization_state_definitions():
    """Tests to make sure that we know the possible polarization states"""
    # The two names of the allowed states
    correct_polarization_state_names = ["Horizontal", "Vertical"]
    for (correct_polarization_name, found_polarization) in zip(correct_polarization_state_names, PolarizationState, strict=True):
        assert correct_polarization_name == found_polarization.name


def test_power_meter_name_definitions():
    """Tests to make sure that we know the possible power meter label states"""
    # The two names of the allowed states
    correct_power_meter_label_names = ["A", "B"]
    for (correct_power_meter_label, found_power_meter_label) in zip(correct_power_meter_label_names, PowerMeterLabel, strict=True):
        assert correct_power_meter_label == found_power_meter_label.name
