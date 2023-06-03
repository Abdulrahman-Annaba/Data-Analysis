"""A module which contains definitions and functions for a beam splitter"""
import pandas as pd

from data_analysis.experiment.definitions import PowerMeterLabel


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
    
    def 