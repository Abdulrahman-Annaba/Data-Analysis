from pathlib import Path

from data_analysis.experiment.beam_splitter import *
from data_analysis.measurement.newport_power_meter import NewportModel835PowerMeterMeasurements
from data_analysis.measurement.thorlabs_power_meter import ThorLabsPM100A_S120VC_PowerMeterMeasurement

def test_beam_splitter_initialization():
    """Test the beam splitter class initialization method"""
    # Setup pandas dataframe from experiment folder
    computation_csv_path = Path("../Trials/GH13-12V (DOWN) (5)/computation_parameters.csv")
    computation_parameters = pd.read_csv(computation_csv_path, index_col=0)
    optical_coefficients = computation_parameters.loc[["A", "B"]][["RV", "RH", "TV", "TH"]]
    # Define transmitted and reflected power meter labels
    transmitted_power_label = PowerMeterLabel.B
    reflected_power_label = PowerMeterLabel.A

    # Create BeamSplitter. Test fails if an exception is raised.
    beam_splitter = BeamSplitter(optical_coefficients, transmitted_power_label, reflected_power_label)

    # Create intentionally malformed optical_coefficients, which is missing the Transmitted coefficients in the Horizontal Polarization state
    optical_coefficients = optical_coefficients.loc[["A", "B"]][["RV", "RH", "TV"]]
    # Create a new beam splitter and confirm that the error is made
    try:
        beam_splitter = BeamSplitter(optical_coefficients, transmitted_power_label, reflected_power_label)
        # If we get to this line, we fail the test since no error was raised within BeamSplitter
        assert False
    except InvalidOpticalCoefficientsFormat:
        # The error was successfully caught
        assert True

def test_incident_power():
    """Tests the incident power method"""
    # Get some data from a trial
    trial_path = Path("../Trials/GH13-12V (DOWN) (5)")
    data = pd.read_csv(trial_path / "data.csv", header=None).to_numpy()
    computation_parameters = pd.read_csv(trial_path / "computation_parameters.csv", index_col=0)
    optical_coefficients = computation_parameters.loc[["A", "B"]][["RV", "RH", "TV", "TH"]]
    transmitted_power = data[:, 2]
    reflected_power = data[:, 1]
    transmitted_power_label = PowerMeterLabel.B
    reflected_power_label = PowerMeterLabel.A
    # Make BeamSplitter
    beam_splitter = BeamSplitter(optical_coefficients, transmitted_power_label, reflected_power_label)
    # Make power meter measurements
    transmitted_power = NewportModel835PowerMeterMeasurements(transmitted_power)
    reflected_power = ThorLabsPM100A_S120VC_PowerMeterMeasurement(reflected_power, at_wavelength=637.8)
    polarization = PolarizationState.Horizontal
    transmitted_power_background = NewportModel835PowerMeterMeasurements(np.array([float(computation_parameters.loc["B"]["Background Power (W)"])]))
    reflected_power_background = ThorLabsPM100A_S120VC_PowerMeterMeasurement(np.array([float(computation_parameters.loc["A"]["Background Power (W)"])]), 637.8)
    incident_power = beam_splitter.compute_incident_power(
        polarization,
        transmitted_power, # type: ignore
        reflected_power, # type: ignore
        transmitted_power_background, # type: ignore
        reflected_power_background # type: ignore
    ) # Added type ignore because pylance was having a moment
    print(incident_power)

def test_efficiency():
    """Tests the efficiency method"""
    # Get some data from a trial
    trial_path = Path("../Trials/GH13-12V (DOWN) (5)")
    data = pd.read_csv(trial_path / "data.csv", header=None).to_numpy()
    computation_parameters = pd.read_csv(trial_path / "computation_parameters.csv", index_col=0)
    optical_coefficients = computation_parameters.loc[["A", "B"]][["RV", "RH", "TV", "TH"]]
    transmitted_power = data[:, 2]
    reflected_power = data[:, 1]
    transmitted_power_label = PowerMeterLabel.B
    reflected_power_label = PowerMeterLabel.A
    # Make BeamSplitter
    beam_splitter = BeamSplitter(optical_coefficients, transmitted_power_label, reflected_power_label)
    # Make power meter measurements
    transmitted_power = NewportModel835PowerMeterMeasurements(transmitted_power)
    reflected_power = ThorLabsPM100A_S120VC_PowerMeterMeasurement(reflected_power, at_wavelength=637.8)
    polarization = PolarizationState.Horizontal
    transmitted_power_background = NewportModel835PowerMeterMeasurements(np.array([float(computation_parameters.loc["B"]["Background Power (W)"])]))
    reflected_power_background = ThorLabsPM100A_S120VC_PowerMeterMeasurement(np.array([float(computation_parameters.loc["A"]["Background Power (W)"])]), 637.8)
    efficiency = beam_splitter.compute_efficiency(
        polarization,
        transmitted_power, # type: ignore
        reflected_power, # type: ignore
        transmitted_power_background, # type: ignore
        reflected_power_background # type: ignore
    ) # Added type ignore because pylance was having a moment
    print(efficiency)