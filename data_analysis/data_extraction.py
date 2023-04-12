"""Module focused on extracting information from a provided trial folder and converting it into a trial instance from the data_computation module."""

# Import some nice to have stuff from trial extraction, like pandas, Path objects, and numpy
import pandas
from pathlib import Path
import numpy

# Import the data_computation module
import data_analysis.data_computation as data_computation
import data_analysis.theory as theoretical


class NoPolarizationSpecifiedError(Exception):
    """Error to be raised if no polarization is found in the dataset"""
    pass

class GratingParameterFileError(Exception):
    """Error to be raised if there is an error reading grating_parameters.csv file."""
    pass

class MissingGratingParameters(Exception):
    """Error to be raised if there are missing parameters in the grating_parameters.csv file."""
    pass

def extract_trial_info(
    trial_folder: Path,
    power_a_column:int = 1,
    power_b_column:int = 2,
    grating_angle_column:int = 3,
    mirror_angle_column:int = 4,
    trial_name:str = ""):
    """This extracts the trial information from the trial folder. Return value should be a Trial instance from the data_computation module"""
    
    # Read in the data from the data csv file as a numpy array.
    data = pandas.read_csv(trial_folder / "data.csv", header=None).iloc[:].to_numpy(dtype=numpy.double)
    # Read in the computation parameters csv file as a pandas dataframe (basically like excel sheet)
    computation_parameters = pandas.read_csv(trial_folder / "computation_parameters.csv", index_col=0)
    # Select a portion of the computation_parameters dataframe that contains the reflectivity and transmittivity coefficients for the glass slide (as a pandas dataframe)
    slide_coefficients = computation_parameters.loc[["A", "B"]][["RH", "TH", "RV", "TV"]]
    polarization:str = computation_parameters.loc["A"]["Polarization"]
    # Select the grating angle offset from the computation_parameters csv file
    grating_angle_offset = computation_parameters["Grating Angle Offset"].loc["A"] #For shifting the grating motor angle's origin to set incidence angle to zero rather than something else
    # Select the background power for sensors A and B from the computation_parameters csv file
    sensor_a_background = computation_parameters["Background Power (W)"].loc["A"]
    sensor_b_background = computation_parameters["Background Power (W)"].loc["B"]
    # If no trial name is specified, use the name of the folder as the trial_label
    trial_label = trial_name if trial_name != "" else trial_folder.name

    # get the appropriate efficiency and incident power functions
    efficiency_function = 0
    incident_power_function = 0
    if polarization.startswith("H"):
        efficiency_function = data_computation.default_horizontal_efficiency
        incident_power_function = data_computation.default_horizontal_incident_power
    elif polarization.startswith("V"):
        efficiency_function = data_computation.default_vertical_efficiency
        incident_power_function = data_computation.default_vertical_incident_power
    else:
        raise NoPolarizationSpecifiedError
    # Construct the Trial object from the data_computation module.
    return data_computation.Trial(
        trial_label,
        data,
        incident_power_function,
        efficiency_function,
        slide_coefficients,
        sensor_a_background,
        sensor_b_background,
        power_a_column=power_a_column,
        power_b_column=power_b_column,
        grating_angle_column=grating_angle_column,
        mirror_angle_column=mirror_angle_column
    )

def extract_grating_info(trial_folder: Path):
    """Extracts grating parameters and returns an instance of Grating."""
    try:
        grating_params = pandas.read_csv(trial_folder / "grating_parameters.csv")
    except:
        raise GratingParameterFileError
    try:
        groove_spacing = int(grating_params["groove_spacing"])
        e_m = float(grating_params["e_m"])
        wavelength = float(grating_params["wavelength"])
        e_d = float(grating_params["e_d"])
        epsilon = float(grating_params["epsilon"])
    except KeyError:
        raise MissingGratingParameters
    return theoretical.Grating(groove_spacing, e_m, wavelength, e_d, epsilon)

def test_extract_trial_info():
    """Simple test to check that some of the trial info is correct. Expects the directory above the data analysis directory to contain the Trials directory, and inside the Trials directory the GH13-12V (B to the right) (3), which contains the trial data, parameters, and information."""
    trial_folder = Path("../Trials/GH13-12V (B to the right) (3)")
    # Extracts the trial info using the above function.
    trial = extract_trial_info(
        trial_folder,
        data_computation.default_efficiency,
        data_computation.default_horizontal_incident_power
    )
    # Assert stuff. If these fail, that indicates that the extract_trial_info function has errored or the trial folder does not contain a computation_parameters.csv file in the proper format.
    assert trial.trial_label == "GH13-12V (B to the right) (3)"
    assert trial.slide_coefficients.loc["A"]["R"] == 0.05835
    assert trial.slide_coefficients.loc["A"]["T"] == 0.90820
    assert trial.slide_coefficients.loc["B"]["R"] == 0.05778
    assert trial.slide_coefficients.loc["B"]["T"] == 0.90710

def test_extract_grating():
    """Simple test"""
    trial_folder = Path("../Trials/GH13-12V (DOWN) (5)")
    grating = extract_grating_info(trial_folder)
    assert isinstance(grating.e_d, float)
    assert isinstance(grating.e_m, float)
    assert isinstance(grating.groove_spacing, int)
    assert isinstance(grating.wavelength, float)
    assert isinstance(grating.epsilon)