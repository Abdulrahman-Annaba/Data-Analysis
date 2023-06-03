"""Module focused on computing the provided data and providing the arrays (to be plotted)"""

# Import some standard libraries for computation
import numpy as np
import pandas as pd

# Import our Polarization and Label definitions
from data_analysis.experiment.definitions import PolarizationState, PowerMeterLabel

# Import our power meters and the abstraction
from data_analysis.measurement.newport_power_meter import NewportModel835PowerMeterMeasurements
from data_analysis.measurement.thorlabs_power_meter import ThorLabsPM100A_S120VC_PowerMeterMeasurement
from data_analysis.measurement.measurement_definitions import Measurements


class Trial:
    """A class to compute the data from each trial."""

    # Defining some internal constants for the class
    _AVERAGE_MULTIPLIER = 5
    """The multiplicative factor to use when computing a sequenced average"""

    _BIN_AVERAGE_BINS = np.array([10**i for i in range(-10, 11, 1)])
    """Defines the boundary values for each bin in a histogram. Each value is separated by a power of 10"""

    def __init__(self,
                 trial_label: str,
                 full_data_set: np.ndarray,
                 slide_coefficients: Slide,
                 polarization_state: PolarizationState,
                 transmitted_power_background: Measurements,
                 reflected_power_background: Measurements,
                 transmitted_power_column: int = 1,
                 reflected_power_column: int = 2,
                 incident_angle_column: int = 3,
                 mirror_angle_column: int = 4,
                 ):
        """Creates a trial. The column parameters refer to the column positions in the numpy array to extract the corresponding values.

        :param trial_label: The label to give the trial
        :param full_data_set: The entire dataset containing all the data collected by the experimental apparatus. This should be a pandas dataframe which has no headers and in which each column can be found.
        :param polarization_state: The polarization that was used in the experiment.
        :param s
        """
        self.data = full_data_set
        self.trial_label = trial_label
        self.power_a_column = power_a_column
        self.power_b_column = power_b_column
        self.grating_angle_column = grating_angle_column
        self.mirror_angle_column = mirror_angle_column
        self.grating_angle_offset = grating_angle_offset
        self.slide_coefficients = slide_coefficients
        self.sensor_a_background = sensor_a_background
        self.sensor_b_background = sensor_b_background

    def compute_efficiency_vs_mirror_angle(self,
                                           grating_angles_to_use=None,
                                           remove_unphysical_points: bool = False,
                                           background_threshold: float = 0):
        """Computes the efficiency vs mirror angle for the given grating angles. The provided grating angles must be explicitly present in the data.

        If remove_unphysical_points is True, this removes the points that have efficiencies outside the domain [0, 1]. This defaults to False.
        If background_threshold is provided, efficiencies below this number are omitted."""

        # If no grating angles were explicitly provided in the method call, get all the grating angles in the data
        if grating_angles_to_use is None:
            grating_angles_to_use = np.unique(
                self.data[:, self.grating_angle_column])
        # Initialize a dictionary to return data in the form Grating angle: numpy array of powers vs. mirror angles
        result = dict()
        # Loop over grating angles
        for grating_angle in grating_angles_to_use:
            # Get a given grating angle's data
            single_run = self.data[self.data[:,
                                             self.grating_angle_column] == grating_angle]
            # Get the unique mirror angles for the specific grating angles. Warning: This sorts the array, even though it might not be sorted in the data sheet
            mirror_angles = np.unique(
                single_run[:, self.mirror_angle_column], axis=0)

            # Initialize a numpy array to place the averaged values for each grating angle. This initializes a 2D array with enough rows to include all mirror_angles, and with 4 columns: mirror angle, power a, power b, incident power
            avg_powers_vs_mirror_angles = np.zeros((1, 3))

            # Loop over mirror angles
            for mirror_angle in mirror_angles:
                # Get the data corresponding to a single mirror step. Warning: this assumes that the elements of the set of mirror angles in each grating angle set of data is unique.
                single_step = single_run[single_run[:,
                                                    self.mirror_angle_column] == mirror_angle]
                # Get the powers
                power_a = single_step[:, self.power_a_column]
                power_b = single_step[:, self.power_b_column]
                # Average the powers
                avg_power_a = self._average(power_a)
                avg_power_b = self._bin_average(power_b)
                # Now stack the values into a 1x3 array and append it to avg_powers_vs_mirror_angles along the 0th axis
                element = np.column_stack(
                    (mirror_angle, avg_power_a, avg_power_b))
                avg_powers_vs_mirror_angles = np.append(
                    avg_powers_vs_mirror_angles, element, axis=0)

            # Remove initialized value
            avg_powers_vs_mirror_angles = avg_powers_vs_mirror_angles[1:]
            # now compute efficiency
            power_a = avg_powers_vs_mirror_angles[:, 1]
            power_b = avg_powers_vs_mirror_angles[:, 2]
            efficiency = self.efficiency(self, power_a, power_b)
            # Now stack arrays together back into the right format
            avg_efficiencies_vs_mirror_angles = np.column_stack(
                (avg_powers_vs_mirror_angles[:, 0], efficiency))

            result.update(
                {
                    f"{str(grating_angle-self.grating_angle_offset)}": avg_efficiencies_vs_mirror_angles
                }
            )

        return result

    def compute_efficiency_vs_incident_angle(self,
                                             grating_angles_to_use=None,
                                             remove_unphysical_points: bool = False,
                                             background_threshold: float = 0):
        """Computes the efficiency vs incident angle for the given grating angles. The provided grating angles must be explicitly present in the data.

        If remove_unphysical_points is True, this removes the points that have efficiencies outside the domain [0, 1]. This defaults to False.
        If background_threshold is provided, efficiencies below this number are omitted.
        """

        # If no grating angles were explicitly provided in the method call, get all the grating angles in the data
        if grating_angles_to_use is None:
            grating_angles_to_use = np.unique(
                self.data[:, self.grating_angle_column])
        # Call the method that computes the things we want, but for each mirror angle. We know this returns a dictionary of Grating angle : efficiencies
        # Then, simply sum the efficiencies in each value of the returned dictionary.
        efficiencies_vs_mirror_angle = self.compute_efficiency_vs_mirror_angle(
            grating_angles_to_use,
            remove_unphysical_points=remove_unphysical_points,
            background_threshold=background_threshold
        )

        # Initialize array
        efficiency_vs_incident_angle = np.zeros((1, 2))
        # Loop over data
        for grating_angle, efficiency_data in efficiencies_vs_mirror_angle.items():
            # Make it a float (since we got this from the key in a dictionary)
            grating_angle = float(grating_angle)
            # Grating angle and incident angle are related simply by an axis inversion.
            incident_angle = -1*grating_angle
            # Sum efficiencies over mirror angles to get one value per grating angle
            efficiency = np.sum(efficiency_data[:, 1], axis=0)
            element = np.column_stack((incident_angle, efficiency))
            efficiency_vs_incident_angle = np.append(
                efficiency_vs_incident_angle, element, axis=0)

        # Remove initialize value
        efficiency_vs_incident_angle = efficiency_vs_incident_angle[1:]
        return efficiency_vs_incident_angle

    def compute_powers_vs_mirror_angle(self,
                                       grating_angles_to_use=None,
                                       background_threshold: float = 0,
                                       power_scale_factor: float = 1):
        """Computes the powers vs mirror angle for the given grating angles. The provided grating angles must be explicitly present in the data.

        If background_threshold is provided, powers below this number (in units of power_scale_factor) are omitted.
        If power_scale_factor is provided, the power readings will all be scaled by this factor."""

        # Initialize a dictionary to return data in the form Grating angle: numpy array of powers vs. mirror angles
        result = dict()
        # If no grating angles were explicitly provided in the method call, get all the grating angles in the data
        if grating_angles_to_use is None:
            grating_angles_to_use = np.unique(
                self.data[:, self.grating_angle_column])
        # Loop over grating angles
        for grating_angle in grating_angles_to_use:
            # Get a given grating angle's data
            single_run = self.data[self.data[:,
                                             self.grating_angle_column] == grating_angle]
            # Get the unique mirror angles for the specific grating angles. Warning: This sorts the array, even though it might not be sorted in the data sheet
            mirror_angles = np.unique(
                single_run[:, self.mirror_angle_column], axis=0)

            # Initialize a numpy array to place the averaged values for each grating angle. This initializes a 2D array with enough rows to include all mirror_angles, and with 4 columns: mirror angle, power a, power b, incident power
            avg_powers_vs_mirror_angles = np.zeros((1, 4))

            # Loop over mirror angles
            for mirror_angle in mirror_angles:
                # Get the data corresponding to a single mirror step. Warning: this assumes that the elements of the set of mirror angles in each grating angle set of data is unique.
                single_step = single_run[single_run[:,
                                                    self.mirror_angle_column] == mirror_angle]
                # Get the powers
                power_a = single_step[:, self.power_a_column]
                power_b = single_step[:, self.power_b_column]
                power_incident = self.incident_power(self, power_a, power_b)
                # Average the powers
                avg_power_a = self._average(power_a)
                avg_power_b = self._bin_average(power_b)
                avg_power_incident = self._average(power_incident)
                # Now stack the values into a 1x4 array and append it to avg_powers_vs_mirror_angles along the 0th axis
                element = np.column_stack(
                    (mirror_angle, avg_power_a, avg_power_b, avg_power_incident))
                avg_powers_vs_mirror_angles = np.append(
                    avg_powers_vs_mirror_angles, element, axis=0)

            # Remove initialized value
            avg_powers_vs_mirror_angles = avg_powers_vs_mirror_angles[1:]
            # multiply the datapoints by the power_scale_factor
            avg_powers_vs_mirror_angles *= power_scale_factor
            # Divide by the same factor for the mirror angles row to account for the fact that we don't scale angles
            avg_powers_vs_mirror_angles[:, 0] /= power_scale_factor

            result.update(
                {
                    f"{str(grating_angle-self.grating_angle_offset)}": avg_powers_vs_mirror_angles
                }
            )

        return result

    def _average(self, power: np.ndarray):
        """Private method to compute the average power. If the power is bad even after doing the succeeding averages, then a custom exception is raised (NoAveragePossibleException)."""
        # Compute the first average power
        first_average = np.average(power, axis=0)
        # Select power values that are less than 5 times the first average
        power = power[power < first_average*self._AVERAGE_MULTIPLIER]
        # Select power values that are greater than 1/5 the first average
        power = power[power > first_average*1/self._AVERAGE_MULTIPLIER]
        # If the last conditional slice resulted in 0 power readings that were close to the first average
        if len(power) == 0:
            raise NoAveragePossibleException
        # Return the final average. This assumes that the previous steps removed the extremal values
        return np.average(power, axis=0)

    def _bin_average(self, power: np.ndarray):
        """Private method to compute the power in cases where we have 1 (maybe 2) outliers that are order of magnitude from the rest. Essentially this is taking the mode and then averaging the most frequent values."""
        # Map the power to the bin it resides in. Bins are specified via BIN_AVERAGE_BINS
        digits = np.digitize(power, self._BIN_AVERAGE_BINS)
        # Find the most frequent bin. This assumes there is only one most frequent bin.
        unique_bins, counts = np.unique(digits, return_counts=True)
        most_frequent_bin = unique_bins[np.argmax(counts)]
        # Get the most frequent bin powers
        most_frequent_powers = power[digits == most_frequent_bin]
        # If there are no most frequent powers, raise NoAveragePossibleException. Otherwise, return the average power
        if len(most_frequent_powers) == 0:
            raise NoAveragePossibleException
        return np.average(most_frequent_powers)


def default_horizontal_incident_power(trial: Trial, power_a, power_b):
    """Default incident power function. Assumes power sensor A is measuring the reflected power off the slide. This uses the first value for power sensor A in the entire trial, since power sensor A is faulty"""
    reflectivity = trial.slide_coefficients.loc["A"]["RH"]  # Get the reflection coefficient for sensor A
    return (power_a - trial.sensor_a_background)/reflectivity


def default_vertical_incident_power(trial: Trial, power_a, power_b):
    """Default incident power function. Assumes power sensor A is measuring the reflected power off the slide. This uses the first value for power sensor A in the entire trial, since power sensor A is faulty"""
    reflectivity = trial.slide_coefficients.loc["A"]["RV"]  # Get the reflection coefficient for sensor A
    return (power_a - trial.sensor_a_background)/reflectivity


def default_horizontal_efficiency(trial: Trial, power_a, power_b):
    """Default efficiency function. This uses the first value for power sensor A in the entire trial, since power sensor A is faulty"""
    reflectivity = trial.slide_coefficients.loc["A"]["RH"]
    result = (power_b-trial.sensor_b_background)/(((power_a - trial.sensor_a_background) /
                                                   reflectivity) - (power_a - trial.sensor_a_background))
    return result


def default_vertical_efficiency(trial: Trial, power_a, power_b):
    """Default efficiency function. This uses the first value for power sensor A in the entire trial, since power sensor A is faulty"""
    reflectivity = trial.slide_coefficients.loc["A"]["RV"]
    result = (power_b-trial.sensor_b_background)/(((power_a - trial.sensor_a_background) /
                                                   reflectivity) - (power_a - trial.sensor_a_background))
    return result


class NoAveragePossibleException(Exception):
    """An exception to be raised when no sequential average is possible."""
    pass
