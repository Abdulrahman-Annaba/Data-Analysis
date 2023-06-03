use crate::experiment::trial::PowerMeterLabel;
use crate::measurement::power_measurement::traits::{
    ArithmeticOps, Background, Efficiency, IncidentPower, Measurement,
};

use crate::experiment::trial::PolarizationState;

use ndarray::Array2;

pub struct Slide<NumberType: ArithmeticOps> {
    optical_coefficients: Array2<NumberType>,
}

impl Slide<f64> {
    fn get_reflectivity_column_index(&self, polarization: &PolarizationState) -> usize {
        match polarization {
            PolarizationState::Horizontal => 0,
            PolarizationState::Vertical => 2,
        }
    }

    fn get_sensor_label_row_index(&self, sensor_label: &PowerMeterLabel) -> usize {
        match sensor_label {
            PowerMeterLabel::SensorA => 0,
            PowerMeterLabel::SensorC => 1,
        }
    }
}

// Define IncidentPower for a slide. This takes the reflected and transmitted powers and the polarization and computes a power result
impl IncidentPower<f64> for Slide<f64> {
    fn compute_incident_power<R, Br, T, Tr>(
        &self,
        reflected_power: &R,
        reflected_power_background: &Br,
        reflected_power_meter_label: &PowerMeterLabel,
        _transmitted_power: &T,
        _transmitted_power_background: &Tr,
        _transmitted_power_meter_label: &PowerMeterLabel,
        polarization: &PolarizationState,
    ) -> f64
    where
        R: Measurement<f64>,
        Br: Background<f64>,
        Tr: Background<f64>,
        T: Measurement<f64>,
    {
        let reflectivity_coefficient = *self
            .optical_coefficients
            .get((
                self.get_sensor_label_row_index(reflected_power_meter_label),
                self.get_reflectivity_column_index(polarization),
            ))
            .expect("Invalid optical coefficients in computation_parameters.csv");

        (reflected_power.value() - reflected_power_background.background())
            / reflectivity_coefficient
    }
}

// Define IncidentPower for a slide. This takes the reflected and transmitted powers and the polarization and computes an efficiency
impl Efficiency<f64> for Slide<f64> {
    fn compute_efficiency<R, Br, T, Tr>(
        &self,
        reflected_power: &R,
        reflected_power_background: &Br,
        reflected_power_meter_label: &PowerMeterLabel,
        transmitted_power: &T,
        transmitted_power_background: &Tr,
        _transmitted_power_meter_label: &PowerMeterLabel,
        polarization: &PolarizationState,
    ) -> f64
    where
        R: Measurement<f64>,
        Br: Background<f64>,
        Tr: Background<f64>,
        T: Measurement<f64>,
    {
        let reflectivity_coefficient = *self
            .optical_coefficients
            .get((
                self.get_sensor_label_row_index(reflected_power_meter_label),
                self.get_reflectivity_column_index(polarization),
            ))
            .expect("Invalid optical coefficients in computation_parameters.csv");

        // (power_b-trial.sensor_b_background)/(((power_a - trial.sensor_a_background)/reflectivity) - (power_a - trial.sensor_a_background))
        (transmitted_power.value() - transmitted_power_background.background())
            / ((reflected_power.value() - reflected_power_background.background())
                / reflectivity_coefficient
                - (reflected_power.value() - reflected_power_background.background()))
    }
}

#[cfg(tests)]
mod tests {
    use super::*;
}
