# get same imports from data extraction
from data_analysis.data_extraction import *
from data_analysis.data_computation import Trial
from data_analysis.experiment.definitions import PolarizationState


def test_extract_trial_info():
    """Simple test to check that some of the trial info is correct. Expects the directory above the data analysis directory to contain the Trials directory, and inside the Trials directory the GH13-12V (B to the right) (3), which contains the trial data, parameters, and information."""
    trial_folder = Path("../Trials/GH13-12V (DOWN) (5)")
    # Extracts the trial info using the above function.
    trial = extract_trial_info(trial_folder)
    # Check that we indeed have a trial object
    assert isinstance(trial, Trial)
    # Assert stuff. If these fail, that indicates that the extract_trial_info function has errored or the trial folder does not contain a computation_parameters.csv file in the proper format.
    assert trial.trial_label == "GH13-12V (DOWN) (5)"
    assert trial.polarization == PolarizationState.Horizontal
    assert trial.beam_splitter.optical_coefficients.loc["A"]["RH"] == 0.05770
    assert trial.beam_splitter.optical_coefficients.loc["A"]["TH"] == 0.90088
    assert trial.beam_splitter.optical_coefficients.loc["A"]["RV"] == 0.09828
    assert trial.beam_splitter.optical_coefficients.loc["A"]["TV"] == 0.88649
    assert trial.beam_splitter.optical_coefficients.loc["B"]["RH"] == 0.05776
    assert trial.beam_splitter.optical_coefficients.loc["B"]["TH"] == 0.90472
    assert trial.beam_splitter.optical_coefficients.loc["B"]["RV"] == 0.09954
    assert trial.beam_splitter.optical_coefficients.loc["B"]["TV"] == 0.87219


def test_extract_grating():
    """Tests the extraction of grating parameters"""
    trial_folder = Path("../Trials/GH13-12V (DOWN) (5)")
    grating = extract_grating_info(trial_folder)
    assert isinstance(grating.e_d, float)
    assert isinstance(grating.e_m, float)
    assert isinstance(grating.groove_spacing, int)
    assert isinstance(grating.wavelength, float)
    assert isinstance(grating.epsilon, float)
