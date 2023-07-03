"""Module focused on extracting information from a provided trial folder and converting it into a trial instance from the data_computation module."""

# Import some nice to have stuff, like pandas, Path objects, and numpy
import pandas
from pathlib import Path
import numpy as np

# Import the data_computation module and the theoretical computation module
import data_analysis.data_computation as data_computation
import data_analysis.theory as theoretical
# Import the beam splitter
from data_analysis.experiment.beam_splitter import BeamSplitter
# Import definitions
from data_analysis.experiment.definitions import PowerMeterLabel, PolarizationState
# Import the possible errors
from data_analysis.extraction_errors import *
# Import the power meters
from data_analysis.measurement.newport_power_meter import NewportModel835PowerMeterMeasurements
from data_analysis.measurement.thorlabs_power_meter import ThorLabsPM100A_S120VC_PowerMeterMeasurement


def extract_trial_info(
        trial_folder: Path,
        transmitted_power_column: int = 2,
        reflected_power_column: int = 1,
        incident_angle_column: int = 3,
        mirror_angle_column: int = 4,
        trial_name: str = None):  # type: ignore
    """Extracts trial information from a trial folder. Must contain a data.csv file and a computation_parameters.csv file. See the README for more information.

    :param trial_folder: A path to a trial folder containing the specified files.
    :param transmitted_power_column: An integer denoting which column of the data contains the transmitted powers
    :param reflected_power_column: An integer denoting which column of the data contains the reflected powers
    :param incident_angle_column: An integer denoting which column of the data contains the incident angles
    :param mirror_angle_column: An integer denoting which column of the data contains the mirror angles
    :param trial_name: The label for the trial. Defaults to the folder name.

    Returns:
    An instance of a trial.
    """

    # Read in the data from the data csv file as a numpy array.
    data = pandas.read_csv(trial_folder / "data.csv",
                           header=None).iloc[:].to_numpy(dtype=np.double)
    # Read in the computation parameters csv file as a pandas dataframe
    computation_parameters = pandas.read_csv(
        trial_folder / "computation_parameters.csv", index_col=0)
    # Select a portion of the computation_parameters dataframe that contains the reflectivity and transmittivity coefficients for the glass slide (as a pandas dataframe)
    slide_coefficients = computation_parameters.loc[[
        "A", "B"]][["RH", "TH", "RV", "TV"]]
    # Initialize the beam splitter. Fails if there are any missing coefficients
    # TODO: Consider reworking this instead of hard coding transmitted and reflected power meter labels
    beam_splitter = BeamSplitter(
        slide_coefficients, PowerMeterLabel.B, PowerMeterLabel.A)
    # Get the polarization
    polarization = computation_parameters.loc["A"]["Polarization"]
    # Check if the polarization is valid
    polarization = get_polarization(polarization)
    # Select the background power for sensors A and B from the computation_parameters csv file
    transmitted_power_background = computation_parameters["Background Power (W)"].loc[
        "B"]
    transmitted_power_background = NewportModel835PowerMeterMeasurements(
        np.array([transmitted_power_background]))
    reflected_power_background = computation_parameters["Background Power (W)"].loc[
        "A"]
    # TODO: Consider reworking this instead of hard coding the wavelength
    reflected_power_background = ThorLabsPM100A_S120VC_PowerMeterMeasurement(
        np.array([reflected_power_background]), 637.8)
    # If no trial name is specified, use the name of the folder as the trial_label
    trial_label = trial_name if trial_name is not None else trial_folder.name
    # Construct the Trial object from the data_computation module.
    return data_computation.Trial(
        trial_label=trial_label,
        full_data_set=data,
        beam_splitter=beam_splitter,
        polarization_state=polarization,
        transmitted_power_background=transmitted_power_background,  # type: ignore
        reflected_power_background=reflected_power_background,  # type: ignore
        transmitted_power_column=transmitted_power_column,
        reflected_power_column=reflected_power_column,
        incident_angle_column=incident_angle_column,
        mirror_angle_column=mirror_angle_column
    )


def extract_grating_info(trial_folder: Path):
    """Extracts grating parameters and returns an instance of Grating."""
    try:
        grating_params = pandas.read_csv(
            trial_folder / "grating_parameters.csv")
    except:
        raise GratingParameterFileError
    try:
        groove_spacing = int(grating_params["groove_spacing"])  # type: ignore
        e_m = float(grating_params["e_m"])  # type: ignore
        wavelength = float(grating_params["wavelength"])  # type: ignore
        e_d = float(grating_params["e_d"])  # type: ignore
        epsilon = float(grating_params["epsilon"])  # type: ignore
    except KeyError:
        raise MissingGratingParameters
    return theoretical.Grating(groove_spacing, e_m, wavelength, e_d, epsilon)


def get_polarization(parsed_polarization: str) -> PolarizationState:
    """Deserializes the given string for a PolarizationState.

    :param parsed_polarization: a string which will be parsed.

    Returns: A PolarizationState variant.

    Raises: `InvalidPolarizationState` if the provided string could not be parsed as a valid state."""

    if parsed_polarization.startswith("H"):
        return PolarizationState.Horizontal
    elif parsed_polarization.startswith("V"):
        return PolarizationState.Vertical
    else:
        raise InvalidPolarizationState
