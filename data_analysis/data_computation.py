"""Module focused on computing the provided data and providing the arrays (to be plotted)"""

# Import some standard libraries for computation
import numpy as np
import pandas as pd
from typing import Dict
from copy import deepcopy

# Import our Polarization and Label definitions
from data_analysis.experiment.definitions import PolarizationState
# Import our beam splitter
from data_analysis.experiment.beam_splitter import BeamSplitter
# Import our interface for power measurements
from data_analysis.measurement.measurement_definitions import Measurements


class Trial:
    """A class to compute the data from each trial."""

    def __init__(self,
                 trial_label: str,
                 full_data_set: np.ndarray,
                 beam_splitter: BeamSplitter,
                 polarization_state: PolarizationState,
                 transmitted_power_background: Measurements,
                 reflected_power_background: Measurements,
                 transmitted_power_column: int = 2,
                 reflected_power_column: int = 1,
                 incident_angle_column: int = 3,
                 mirror_angle_column: int = 4,
                 ):
        """Creates a trial. The column parameters refer to the column positions in the numpy array to extract the corresponding values.

        :param trial_label: The label to give the trial
        :param full_data_set: The entire dataset containing all the data collected by the experimental apparatus. This should be a numpy array which has no headers and in which each column specified in the class constructor can be found
        :param beam_splitter: The beam splitter used in the trial
        :param polarization_state: The polarization that was used in the trial
        :param transmitted_power_background: The background power for the transmitted power meter
        :param reflected_power_background: The background power for the reflected power meter
        :param transmitted_power_column: The index used to find the transmitted power column in `full_data_set`
        :param reflected_power_column: The index used to find the reflected power column in `full_data_set`
        :param incident_angle_column: The index used to find the incident angles in `full_data_set`
        :param mirror_angle_column: The index used to find the mirror angles in `full_data_set`
        """
        self.trial_label = trial_label
        self.data = full_data_set
        self.beam_splitter = beam_splitter
        self.polarization = polarization_state
        self.transmitted_background = transmitted_power_background
        self.reflected_background = reflected_power_background
        self.transmitted_column = transmitted_power_column
        self.reflected_column = reflected_power_column
        self.incident_angle_column = incident_angle_column
        self.mirror_angle_column = mirror_angle_column

    def compute_efficiency_vs_mirror_angle(self,
                                           incident_angles_to_use: np.ndarray = None) -> Dict[float, np.ndarray]:  # type: ignore
        """Computes the efficiency vs mirror angle for the given grating angles. The provided grating angles must be explicitly present in the data.
        If remove_unphysical_points is True, this removes the points that have efficiencies outside the domain [0, 1]. This defaults to False.
        If background_threshold is provided, efficiencies below this number are omitted.

        :param incident_angles_to_use: A numpy 1D array of incident angles. The incident angles must be present in the dataset. Defaults to include all the incident angles present in the data.

        Returns a dictionary where the keys are the incident angles and the values are Nx2 numpy arrays where the columns are (from left to right) the mirror angle and the efficiency
        """
        # Check type of `incident_angles_to_use`
        if incident_angles_to_use is None:
            # grating_angle was an old definition used in old iterations of the program. It is defined as the negative of the incident angle according to the standard grating equation.
            grating_angles_to_use = np.unique(
                self.data[:, self.incident_angle_column]
            )
            incident_angles_to_use = -1*grating_angles_to_use
        # Compute powers vs mirror angles
        powers_vs_mirror_angles = self.compute_powers_vs_mirror_angle(
            incident_angles_to_use)
        # Initialize the return value
        result: Dict[float, np.ndarray] = dict()
        # Loop over the powers vs mirror angles dictionary
        for incident_angle, powers_vs_mirror_angles in powers_vs_mirror_angles.items():
            # Get mirror angles, transmitted power and reflected power
            mirror_angles = powers_vs_mirror_angles[:, 0]
            transmitted_power = powers_vs_mirror_angles[:, 2]
            transmitted_power = self._make_power_measurements(
                self.transmitted_background, transmitted_power)
            reflected_power = powers_vs_mirror_angles[:, 3]
            reflected_power = self._make_power_measurements(
                self.reflected_background, reflected_power)
            # Compute efficiency
            efficiency = self.beam_splitter.compute_efficiency(
                self.polarization, transmitted_power, reflected_power, self.transmitted_background, self.reflected_background)
            # Make value for result
            value = np.column_stack((mirror_angles, efficiency))
            # Append result
            result.update({
                incident_angle: value
            })
        return result

    def compute_efficiency_errors_vs_mirror_angle(self,
                                                  incident_angles_to_use: np.ndarray = None) -> Dict[float, np.ndarray]:  # type: ignore
        """Computes the error in efficiency vs mirror angle for the given incident angles. The provided grating angles must be explicitly present in the data.
        If remove_unphysical_points is True, this removes the points that have efficiencies outside the domain [0, 1]. This defaults to False.
        If background_threshold is provided, efficiencies below this number are omitted.

        :param incident_angles_to_use: A numpy 1D array of incident angles. The incident angles must be present in the dataset. Defaults to include all the incident angles present in the data.

        Returns a dictionary where the keys are the incident angles and the values are Nx2 numpy arrays where the columns are (from left to right) the mirror angle and the error in efficiency
        """
        # Check type of `incident_angles_to_use`
        if incident_angles_to_use is None:
            # grating_angle was an old definition used in old iterations of the program. It is defined as the negative of the incident angle according to the standard grating equation.
            grating_angles_to_use = np.unique(
                self.data[:, self.incident_angle_column]
            )
            incident_angles_to_use = -1*grating_angles_to_use
        # Compute powers vs mirror angles
        powers_vs_mirror_angles = self.compute_powers_vs_mirror_angle(
            incident_angles_to_use)
        # Initialize the return value
        result: Dict[float, np.ndarray] = dict()
        # Loop over the powers vs mirror angles dictionary
        for incident_angle, powers_vs_mirror_angles in powers_vs_mirror_angles.items():
            # Get mirror angles, transmitted power and reflected power
            mirror_angles = powers_vs_mirror_angles[:, 0]
            transmitted_power = powers_vs_mirror_angles[:, 2]
            transmitted_power = self._make_power_measurements(
                self.transmitted_background, transmitted_power)
            reflected_power = powers_vs_mirror_angles[:, 3]
            reflected_power = self._make_power_measurements(
                self.reflected_background, reflected_power)
            # Compute efficiency
            efficiency_err = self.beam_splitter.compute_efficiency_error(
                self.polarization, transmitted_power, reflected_power, self.transmitted_background, self.reflected_background)
            # Make value for result
            value = np.column_stack((mirror_angles, efficiency_err))
            # Append result
            result.update({
                incident_angle: value
            })
        return result

    def compute_efficiency_vs_incident_angle(self,
                                             incident_angles_to_use: np.ndarray = None) -> np.ndarray:  # type: ignore
        """Computes the efficiency vs incident angle for the given incident angles. The provided incident angles must be explicitly present in the data.

        :param incident_angles_to_use: A Nx1 numpy array representing the incident angles to use in the computation.

        Returns a Nx2 numpy array where the columns are (from left to right) the incident angle and the total efficiency 
        """
        # Check type of `incident_angles_to_use`
        if incident_angles_to_use is None:
            # grating_angle was an old definition used in old iterations of the program. It is defined as the negative of the incident angle according to the standard grating equation.
            grating_angles_to_use = np.unique(
                self.data[:, self.incident_angle_column]
            )
            incident_angles_to_use = -1*grating_angles_to_use
        # Compute efficiency vs mirror angles
        efficiency_vs_mirror_angles = self.compute_efficiency_vs_mirror_angle(
            incident_angles_to_use)
        # Initialize a return array for the data
        efficiency_vs_incident_angles = np.zeros((1, 2))
        # Loop over the incident angles and the corresponding efficiency vs mirror angles
        for incident_angle, efficiency_vs_mirror_angles in efficiency_vs_mirror_angles.items():
            # Sum the efficiency across all mirror angles at the given incident angle
            total_efficiency = np.sum(
                efficiency_vs_mirror_angles[:, 1], axis=0)
            # Make the data point
            element = np.column_stack((incident_angle, total_efficiency))
            # Append the data point
            efficiency_vs_incident_angles = np.append(
                efficiency_vs_incident_angles, element, axis=0)
        # Remove the initial value
        efficiency_vs_incident_angles = efficiency_vs_incident_angles[1:]
        # Return the result
        return efficiency_vs_incident_angles

    def compute_efficiency_error_vs_incident_angle(self,
                                                   incident_angles_to_use: np.ndarray = None) -> np.ndarray:  # type: ignore
        """Computes the error in total efficiency vs incident angle for the given incident angles. The provided incident angles must be explicitly present in the data.

        :param incident_angles_to_use: A Nx1 numpy array representing the incident angles to use in the computation.

        Returns a Nx2 numpy array where the columns are (from left to right) the incident angle and the error in the total efficiency 
        """
        # Check type of `incident_angles_to_use`
        if incident_angles_to_use is None:
            # grating_angle was an old definition used in old iterations of the program. It is defined as the negative of the incident angle according to the standard grating equation.
            grating_angles_to_use = np.unique(
                self.data[:, self.incident_angle_column]
            )
            incident_angles_to_use = -1*grating_angles_to_use
        # Compute error in efficiency vs mirror angles
        efficiency_err_vs_mirror_angles = self.compute_efficiency_errors_vs_mirror_angle(
            incident_angles_to_use)
        # Initialize a return array for the data
        efficiency_err_vs_incident_angles = np.zeros((1, 2))
        # Loop over the incident angles and the corresponding efficiency error vs mirror angles
        for incident_angle, efficiency_err_vs_mirror_angles in efficiency_err_vs_mirror_angles.items():
            # Add the individual efficiency errors in quadrature to get the total error in efficiency
            total_efficiency_err = np.sum(
                np.power(efficiency_err_vs_mirror_angles[:, 1], 2), axis=0)
            # Make the data point
            element = np.column_stack((incident_angle, total_efficiency_err))
            # Append the data point
            efficiency_err_vs_incident_angles = np.append(
                efficiency_err_vs_incident_angles, element, axis=0)
        # Remove the initial value
        efficiency_err_vs_incident_angles = efficiency_err_vs_incident_angles[1:]
        # Return the result
        return efficiency_err_vs_incident_angles

    def compute_powers_vs_mirror_angle(self,
                                       incident_angles_to_use: np.ndarray = None,  # type: ignore
                                       power_scale_factor: float = 1) -> Dict[float, np.ndarray]:
        """Computes the powers vs mirror angle for the given grating angles. The provided grating angles must be explicitly present in the data.

        :param incident_angles_to_use: An Nx1 numpy array representing the incident angles to use when computing the error
        :param power_scale_factor: A float which represents a multiplicative factor to apply to the power errors
        If power_scale_factor is provided, the power readings will all be scaled by this factor.

        Returns a dictionary where the keys are the incident angles, and the values are Nx4 shaped numpy arrays where the columns are (from left to right) are mirror angles, incident power, transmitted power, and reflected power.
        """

        # Check type of `incident_angles_to_use`
        if incident_angles_to_use is None:
            # grating_angle was an old definition used in old iterations of the program. It is defined as the negative of the incident angle according to the standard grating equation.
            grating_angles_to_use = np.unique(
                self.data[:, self.incident_angle_column]
            )
            incident_angles_to_use = -1*grating_angles_to_use
        # Initialize the return value
        result: Dict[float, np.ndarray] = dict()
        # Loop over incident angles
        for incident_angle in incident_angles_to_use:
            # grating_angle was an old definition used in old iterations of the program. It is defined as the negative of the incident angle according to the standard grating equation.
            grating_angle = -1*incident_angle
            # Get the data for a single run
            single_run = self.data[self.data[:,
                                             self.incident_angle_column] == grating_angle]
            # Get the unique mirror angles in this data
            mirror_angles = np.unique(
                single_run[:, self.mirror_angle_column], axis=0)
            # Average over the replicates
            avg_powers_vs_mirror_angles = self._avg_replicates(
                single_run, mirror_angles)

            # Get the transmitted and reflected powers as power measurements
            transmitted_power = self._make_power_measurements(
                self.transmitted_background, avg_powers_vs_mirror_angles[:, 1])
            reflected_power = self._make_power_measurements(
                self.reflected_background, avg_powers_vs_mirror_angles[:, 2])
            # Compute the incident power
            incident_power = self.beam_splitter.compute_incident_power(
                self.polarization, transmitted_power, reflected_power, self.transmitted_background, self.reflected_background)
            # Make the value to append to the result
            # Ordering of columns is mirror angles, then incident power, then transmitted power, then reflected power
            value = np.column_stack(
                (avg_powers_vs_mirror_angles[:, 0], incident_power*power_scale_factor, transmitted_power.values*power_scale_factor, reflected_power.values*power_scale_factor))
            # Append the result
            result.update({
                incident_angle: value
            })
        return result

    def compute_power_errors_vs_mirror_angle(self, incident_angles_to_use: np.ndarray, power_scale_factor: float = 1) -> Dict[float, np.ndarray]:
        """
        Computes the one-sided error in incident power, transmitted power, and reflected power for the given incident angles.

        :param incident_angles_to_use: An Nx1 numpy array representing the incident angles to use when computing the error
        :param power_scale_factor: A float which represents a multiplicative factor to apply to the power errors

        Returns a dictionary whose keys are the incident angles and whose values are Nx4 numpy arrays where the columns are (from left to right) the mirror angle, the incident power error, the transmitted power error, and the reflected power error

        """
        # Check type of `incident_angles_to_use`
        if incident_angles_to_use is None:
            # grating_angle was an old definition used in old iterations of the program. It is defined as the negative of the incident angle according to the standard grating equation.
            grating_angles_to_use = np.unique(
                self.data[:, self.incident_angle_column]
            )
            incident_angles_to_use = -1*grating_angles_to_use
        # Initialize the return value
        result: Dict[float, np.ndarray] = dict()
        # Loop over incident angles
        for incident_angle in incident_angles_to_use:
            # grating_angle was an old definition used in old iterations of the program. It is defined as the negative of the incident angle according to the standard grating equation.
            grating_angle = -1*incident_angle
            # Get the data for a single run
            single_run = self.data[self.data[:,
                                             self.incident_angle_column] == grating_angle]
            # Get the unique mirror angles in this data
            mirror_angles = np.unique(
                single_run[:, self.mirror_angle_column], axis=0)
            # Average over the replicates
            avg_powers_vs_mirror_angles = self._avg_replicates(
                single_run, mirror_angles)
            # Get the transmitted and reflected powers as power measurements
            transmitted_power = self._make_power_measurements(
                self.transmitted_background, avg_powers_vs_mirror_angles[:, 1])
            reflected_power = self._make_power_measurements(
                self.reflected_background, avg_powers_vs_mirror_angles[:, 2])
            # Compute the incident power error
            incident_power_err = self.beam_splitter.compute_incident_power_error(
                self.polarization, transmitted_power, reflected_power, self.transmitted_background, self.reflected_background)
            # Make the value to append to the result
            # Ordering of columns is mirror angles, then incident power, then transmitted power, then reflected power
            value = np.column_stack(
                (mirror_angles, incident_power_err*power_scale_factor, transmitted_power.abs_uncertainty()*power_scale_factor, reflected_power.abs_uncertainty()*power_scale_factor))
            # Append the result
            result.update({
                incident_angle: value
            })
        return result

    def _avg_replicates(self, single_run: np.ndarray, mirror_angles: np.ndarray) -> np.ndarray:
        """Averages over the replicates in a single run. Returns a 3 column array containing mirror angles, transmitted power, and reflected power"""
        # Initialize an empty array for the mirror angles and the efficiencies
        avg_powers_vs_mirror_angles: np.ndarray = np.zeros((1, 3))
        # Loop over the mirror angles
        for mirror_angle in mirror_angles:
            # Get the replicate data for each mirror angle
            replicates = single_run[single_run[:,
                                               self.mirror_angle_column] == mirror_angle]
            # Make the power meter types
            transmitted_power = self._make_power_measurements(
                self.transmitted_background, replicates[:, self.transmitted_column])
            reflected_power = self._make_power_measurements(
                self.reflected_background, replicates[:, self.reflected_column])
            # Average the powers
            avg_transmitted_power = transmitted_power.average()
            avg_reflected_power = reflected_power.average()
            # Append powers to avg_powers_vs_mirror_angles
            element = np.column_stack(
                (mirror_angle, avg_transmitted_power, avg_reflected_power))
            avg_powers_vs_mirror_angles = np.append(
                avg_powers_vs_mirror_angles, element, axis=0)
        # Remove the initialized value
        avg_powers_vs_mirror_angles = avg_powers_vs_mirror_angles[1:]
        return avg_powers_vs_mirror_angles

    @staticmethod
    def _make_power_measurements(background: Measurements, data: np.ndarray) -> Measurements:
        """Given the background power measurement and data, return a power meter instance with the specified data.

        :param background: A type which implements `Measurements`
        :param data: The data which is to be stored.
        """
        measurement = deepcopy(background)
        measurement.values = data
        return measurement


class NoAveragePossibleException(Exception):
    """An exception to be raised when no sequential average is possible."""
    pass
