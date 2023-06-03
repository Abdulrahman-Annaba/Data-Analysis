use lazy_static::lazy_static;
use std::collections::HashMap;

use crate::measurement::power_measurement::traits::{AbsoluteUncertainty, Background, Measurement};

// Define the mapping of uncertainty wavelength ranges to their corresponding fractional uncertainties
lazy_static! {
    static ref THORLABS_PM100A_S120VC_WAVELENGTH_UNCERTAINTIES: HashMap<ThorlabsPm100aS120vcUncertaintyWavelengthRange, f64> = {
        let mut map: HashMap<ThorlabsPm100aS120vcUncertaintyWavelengthRange, f64> = HashMap::new();
        map.insert(
            ThorlabsPm100aS120vcUncertaintyWavelengthRange::Range440to980nm,
            0.03,
        );
        map.insert(
            ThorlabsPm100aS120vcUncertaintyWavelengthRange::Range200to279nm,
            0.07,
        );
        map.insert(
            ThorlabsPm100aS120vcUncertaintyWavelengthRange::Range280to439nm,
            0.05,
        );
        map.insert(
            ThorlabsPm100aS120vcUncertaintyWavelengthRange::Range981to1100nm,
            0.07,
        );
        map
    };
}

// Describes the possible wavelength ranges for determining the uncertainty in measurement
#[derive(Hash, PartialEq, Eq)]
enum ThorlabsPm100aS120vcUncertaintyWavelengthRange {
    Range440to980nm,
    Range280to439nm,
    Range200to279nm,
    Range981to1100nm,
}

// Helper method on this enum to return the appropriate variant given a float.
// Will choose to handle wavelengths between enumerations as belonging to the higher wavelength enumeration.
impl ThorlabsPm100aS120vcUncertaintyWavelengthRange {
    fn get_range(at_wavelength: &f64) -> ThorlabsPm100aS120vcUncertaintyWavelengthRange {
        // Find the range the wavelength is in
        match *at_wavelength {
            x if (200.0..=279.0).contains(&x) => {
                ThorlabsPm100aS120vcUncertaintyWavelengthRange::Range200to279nm
            }
            x if x > 279.0 && x <= 439.0 => {
                ThorlabsPm100aS120vcUncertaintyWavelengthRange::Range280to439nm
            }
            x if x > 439.0 && x <= 980.0 => {
                ThorlabsPm100aS120vcUncertaintyWavelengthRange::Range440to980nm
            }
            x if x > 980.0 && x <= 1100.0 => {
                ThorlabsPm100aS120vcUncertaintyWavelengthRange::Range981to1100nm
            }
            _ => panic!("Invalid measurement. Wavelength is out of range."),
        }
    }
}

// Define the thorlabs PM100A S120VC power meter measurement
pub struct ThorLabsPM100A_S120VC_PowerMeterMeasurement {
    // This is the actual power measurement in watts.
    value: f64,
    // This is the wavelength that the measurement was taken at. It is necessary to calculate uncertainty.
    at_wavelength: f64,
}

// Wrapper struct to contain the background measurement
pub struct ThorLabsPM100A_S120VC_PowerMeterMeasurementBackground(f64);

impl Background<f64> for ThorLabsPM100A_S120VC_PowerMeterMeasurementBackground {
    fn background(&self) -> f64 {
        self.0
    }
}
// Here we define the constructor for this power measurement.
impl ThorLabsPM100A_S120VC_PowerMeterMeasurement {
    pub fn new(value: f64, at_wavelength: f64) -> ThorLabsPM100A_S120VC_PowerMeterMeasurement {
        ThorLabsPM100A_S120VC_PowerMeterMeasurement {
            value,
            at_wavelength,
        }
    }
}

// Here we implement the measurement interface for the thorlabs power meter
impl Measurement<f64> for ThorLabsPM100A_S120VC_PowerMeterMeasurement {
    fn value(&self) -> f64 {
        self.value
    }
}

// Here we implement the absolute uncertainty interface for the thorlabs power meter
impl AbsoluteUncertainty<f64> for ThorLabsPM100A_S120VC_PowerMeterMeasurement {
    fn uncertainty(&self) -> f64 {
        let value = &self.value;
        let range = ThorlabsPm100aS120vcUncertaintyWavelengthRange::get_range(&self.at_wavelength);
        let frac_uncertainty = THORLABS_PM100A_S120VC_WAVELENGTH_UNCERTAINTIES
            .get(&range)
            .unwrap();
        // Compute the absolute uncertainty
        value * frac_uncertainty
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_thorlabs_pm100a_s120vc_measurement() {
        // Measurement in watts
        let measurement = 0.01;
        // Convert this into a thorlabs measurement
        let thorlabs_measurement =
            ThorLabsPM100A_S120VC_PowerMeterMeasurement::new(measurement, 637.8);
        // Test value
        assert_eq!(measurement, thorlabs_measurement.value());
        // Test uncertainty according to specification
        let frac_uncertainty = 0.03;
        let correct_measurement_uncertainty = measurement * frac_uncertainty;
        assert_eq!(
            correct_measurement_uncertainty,
            thorlabs_measurement.uncertainty()
        );
    }
}
