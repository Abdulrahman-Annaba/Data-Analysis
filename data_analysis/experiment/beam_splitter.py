"""A module which contains definitions and functions for a beam splitter"""
import pandas as pd
import numpy as np

from data_analysis.experiment.definitions import PowerMeterLabel, PolarizationState
from data_analysis.measurement.measurement_definitions import Measurements


class InvalidOpticalCoefficientsFormat(Exception):
    """An exception raised when there is a formatting error in the provided optical coefficients dataframe"""


class BeamSplitter:
    """An object which behaves as a beam splitter, with reflectivity and transmittivity coefficients."""

    def __init__(self, optical_coefficients: pd.DataFrame, transmitted_power_meter_label: PowerMeterLabel, reflected_power_meter_label: PowerMeterLabel):
        """Creates a beam splitter.

        :param optical_coefficients: A pandas dataframe containing columns representing the transmittivity and reflectivity coefficients for both power meters and both polarization states.
        :param transmitted_power_meter_label: The power meter label designation for the transmitted power
        :param reflected_power_meter_label: The power meter label designation for the reflected power
        """
        # Check that we have both power meter labels present
        try:
            optical_coefficients.loc[transmitted_power_meter_label.name]
        except KeyError:
            raise InvalidOpticalCoefficientsFormat(
                f"No row specifying {transmitted_power_meter_label.name} found in optical coefficients.")
        try:
            optical_coefficients.loc[reflected_power_meter_label.name]
        except KeyError:
            raise InvalidOpticalCoefficientsFormat(
                f"No row specifying {reflected_power_meter_label.name} found in optical coefficients.")
        # Check that we have each optical coefficient for each polarization state
        for i in ["RV", "RH", "TV", "TH"]:
            try:
                optical_coefficients[i]
            except KeyError:
                raise InvalidOpticalCoefficientsFormat(
                    f"Required column '{i}' specifying an optical coefficient not found in optical coefficients.")
        # Finally, store the optical coefficients and power meter labels.
        self.optical_coefficients = optical_coefficients
        self.transmitted_power_meter_label = transmitted_power_meter_label
        self.reflected_power_meter_label = reflected_power_meter_label
    
    def compute_incident_power(
            self,
            polarization: PolarizationState,
            transmitted_power: Measurements,
            reflected_power: Measurements,
            transmitted_power_background: Measurements,
            reflected_power_background: Measurements
    ) -> np.ndarray:
        """Compute the incident power on the beam splitter.
        
        :param polarization: The polarization of the incident light
        :param transmitted_power: The transmitted power
        :param reflected_power: The reflected power
        :param transmitted_power_background: Background power of the transmitted power meter
        :param reflected_power_background: Background power of the reflected power meter
        """
        # The columns are of the set ["RV", "RH", "TV", "TH"], so we must construct the proper column name for the reflectivity given the polarization
        column_name = f"R{polarization.name[0]}"
        # Extract the value as a float
        reflectivity_coefficient = float(self.optical_coefficients.loc[self.reflected_power_meter_label.name][column_name])

        # Compute the value of the incident power
        return (reflected_power.values() - reflected_power_background.values())/reflectivity_coefficient
    
    def compute_efficiency(
            self,
            polarization: PolarizationState,
            transmitted_power: Measurements,
            reflected_power: Measurements,
            transmitted_power_background: Measurements,
            reflected_power_background: Measurements
    ) -> np.ndarray:
        """Compute the efficiency of the slide.

        :param polarization: The polarization of the incident light
        :param transmitted_power: The transmitted power
        :param reflected_power: The reflected power
        :param transmitted_power_background: Background power of the transmitted power meter
        :param reflected_power_background: Background power of the reflected power meter
        """
        # The columns are of the set ["RV", "RH", "TV", "TH"], so we must construct the proper column name for the reflectivity given the polarization
        column_name = f"R{polarization.name[0]}"
        # Extract the value as a float
        reflectivity_coefficient = float(self.optical_coefficients.loc[self.reflected_power_meter_label.name][column_name])
        # Compute the efficiency
        return (transmitted_power.values() - transmitted_power_background.values())/((reflected_power.values() - reflected_power_background.values())/reflectivity_coefficient - (reflected_power.values() - reflected_power_background.values()))