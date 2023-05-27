use crate::measurement::power_measurement::{Background, Measurement, PowerMeterLabel};
use ndarray::ScalarOperand;
use ndarray::{Array1, Array2};
use polars::frame::DataFrame;

/// Represents a trial
pub struct Trial<BackgroundT, BackgroundR, NumberType>
where
    BackgroundT: Background<NumberType>,
    BackgroundR: Background<NumberType>,
    NumberType: ScalarOperand,
{
    label: String,
    full_data_set: Array2<NumberType>,
    transmitted_sensor_background: BackgroundT,
    reflected_sensor_background: BackgroundR,
    transmitted_power_column_number: u8,
    transmitted_power_meter_label: PowerMeterLabel,
    reflected_power_column_number: u8,
    reflected_power_meter_label: PowerMeterLabel,
    incident_angle_column: u8,
    mirror_angle_column: u8,
    polarization_state: PolarizationState,
    slide: Slide,
}

struct Slide {
    optical_coefficients: DataFrame,
}

/// An enumeration over the allowed polarization states for light in this experiment.
enum PolarizationState {
    Horizontal,
    Vertical,
}

// Define the IncidentPower interface
trait IncidentPower {
    // Should have a method called compute which takes an immutable reference to itself and computes a value
    // This should accept any two measurements types and return the appropriate value.
    fn compute_incident_power<R, T, V>(
        &self,
        reflected_power: &R,
        reflected_power_meter_label: &PowerMeterLabel,
        transmitted_power: &T,
        transmitted_power_meter_label: &PowerMeterLabel,
        polarization: &PolarizationState,
    ) -> V
    where
        R: Measurement<V>,
        T: Measurement<V>;
}

/// Define the Efficiency interface
trait Efficiency {
    fn compute_efficiency<R, T, V>(
        &self,
        reflected_power: R,
        reflected_power_meter_label: &PowerMeterLabel,
        transmitted_power: T,
        transmitted_power_meter_label: &PowerMeterLabel,
        polarization: PolarizationState,
    ) -> V
    where
        R: Measurement<V>,
        T: Measurement<V>;
}

// Define IncidentPower for a slide. This takes the reflected and transmitted powers and the polarization and computes a power result
impl IncidentPower for Slide {
    fn compute_incident_power<R, T, V>(
        &self,
        reflected_power: &R,
        reflected_power_meter_label: &PowerMeterLabel,
        transmitted_power: &T,
        transmitted_power_meter_label: &PowerMeterLabel,
        polarization: &PolarizationState,
    ) -> V
    where
        R: Measurement<V>,
        T: Measurement<V>,
    {
        let reflectivity_coefficient = { self.optical_coefficients };
        todo!()
    }
}
