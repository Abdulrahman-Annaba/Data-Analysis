"""A module which contains definitions and functions for a beam splitter"""
import pandas as pd
import numpy as np
from copy import deepcopy

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
        reflectivity_coefficient = float(
            self.optical_coefficients.loc[self.reflected_power_meter_label.name][column_name])

        # Compute the value of the incident power
        # Subtract background from raw value, then divide reflected values by the reflectivity coefficient.
        return (reflected_power.values - reflected_power_background.values)/reflectivity_coefficient

    # TEST
    def compute_incident_power_error(
            self,
            polarization: PolarizationState,
            transmitted_power: Measurements,
            reflected_power: Measurements,
            transmitted_power_background: Measurements,
            reflected_power_background: Measurements
    ) -> np.ndarray:
        """
        Compute the error in the incident power on the beam splitter

        :param polarization: The polarization of the incident light
        :param transmitted_power: The transmitted power
        :param reflected_power: The reflected power
        :param transmitted_power_background: Background power of the transmitted power meter
        :param reflected_power_background: Background power of the reflected power meter
        """
        # First compute the incident power
        incident_power = self.compute_incident_power(
            polarization, transmitted_power, reflected_power, transmitted_power_background, reflected_power_background)
        # Compute the variations in the transmitted and reflected powers
        raw_var_transmitted = transmitted_power.values + \
            transmitted_power.abs_uncertainty()
        raw_var_reflected = reflected_power.values + reflected_power.abs_uncertainty()
        # Make them into measurements
        var_transmitted = deepcopy(transmitted_power_background)
        var_transmitted.values = raw_var_transmitted
        var_reflected = deepcopy(reflected_power_background)
        var_reflected.values = raw_var_reflected
        # Compute the variations
        inc_power_var_trans = self.compute_incident_power(
            polarization, var_transmitted, reflected_power, transmitted_power_background, reflected_power_background) - incident_power
        inc_power_var_reflec = self.compute_incident_power(
            polarization, transmitted_power, var_reflected, transmitted_power_background, reflected_power_background) - incident_power
        # Now add in quadrature
        result = np.power(np.power(inc_power_var_trans, 2) +
                          np.power(inc_power_var_reflec, 2), 1/2)
        return result

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
        reflectivity_coefficient = float(
            self.optical_coefficients.loc[self.reflected_power_meter_label.name][column_name])
        # Shorthand values; self explanatory
        T = transmitted_power.values
        R = reflected_power.values
        T_b = transmitted_power_background.values
        R_b = reflected_power_background.values
        # Compute the efficiency
        return (T - T_b)/((R - R_b)/reflectivity_coefficient)

    # TEST
    def compute_efficiency_error(
            self,
            polarization: PolarizationState,
            transmitted_power: Measurements,
            reflected_power: Measurements,
            transmitted_power_background: Measurements,
            reflected_power_background: Measurements
    ) -> np.ndarray:
        """
        Compute the error in the efficiency of the beam splitter

        :param polarization: The polarization of the incident light
        :param transmitted_power: The transmitted power
        :param reflected_power: The reflected power
        :param transmitted_power_background: Background power of the transmitted power meter
        :param reflected_power_background: Background power of the reflected power meter
        """
        # First compute the efficiency
        efficiency = self.compute_efficiency(
            polarization, transmitted_power, reflected_power, transmitted_power_background, reflected_power_background)
        # Compute the variations in the transmitted and reflected powers
        raw_var_transmitted = transmitted_power.values + \
            transmitted_power.abs_uncertainty()
        raw_var_reflected = reflected_power.values + reflected_power.abs_uncertainty()
        # Make them into measurements
        var_transmitted = deepcopy(transmitted_power_background)
        var_transmitted.values = raw_var_transmitted
        var_reflected = deepcopy(reflected_power_background)
        var_reflected.values = raw_var_reflected
        # Compute the variations
        eff_var_trans = self.compute_efficiency(
            polarization, var_transmitted, reflected_power, transmitted_power_background, reflected_power_background) - efficiency
        eff_var_reflec = self.compute_efficiency(
            polarization, transmitted_power, var_reflected, transmitted_power_background, reflected_power_background) - efficiency
        # Now add in quadrature
        result = np.power(np.power(eff_var_trans, 2) +
                          np.power(eff_var_reflec, 2), 1/2)
        return result
