use std::collections::HashMap;
use lazy_static::lazy_static;
use crate::measurement::measurement::{AbsoluteUncertainty, Measurement};

// Defines a power measurement as read from a newport model 835 power meter
pub struct NewportModel835PowerMeterMeasurement {
    // A power measurement should have a float value
    value: f64,
}

impl NewportModel835PowerMeterMeasurement {
    pub fn new(value: f64) -> NewportModel835PowerMeterMeasurement {
        NewportModel835PowerMeterMeasurement { value }
    }
}

// Define a global variable mapping the Newport Model 835 Power Meter ranges to their associated fullscale uncertainties.
lazy_static! {
    pub static ref NEWPORT_MODEL_835_POWER_METER_FULLSCALE_UNCERTAINTIES: HashMap<NewportModel835PowerMeterRange, f64> = {
        let mut map: HashMap<NewportModel835PowerMeterRange, f64> = HashMap::new();
        map.insert(NewportModel835PowerMeterRange::Twonanowatts, 0.002);
        map.insert(NewportModel835PowerMeterRange::Twentynanowatts, 0.0005);
        map.insert(NewportModel835PowerMeterRange::Twohundrednanowatts, 0.0005);
        map.insert(NewportModel835PowerMeterRange::Twomilliwatts, 0.0005);
        map.insert(NewportModel835PowerMeterRange::Twentymilliwatts, 0.0005);
        map.insert(NewportModel835PowerMeterRange::Twohundredmilliwatts, 0.0005);
        map
    };
}

// Define a global variable mapping the Newport Model 835 Power Meter ranges to their associated reading uncertainties.
lazy_static! {
    pub static ref NEWPORT_MODEL_835_POWER_METER_READING_UNCERTAINTIES: HashMap<NewportModel835PowerMeterRange, f64> = {
        let mut map: HashMap<NewportModel835PowerMeterRange, f64> = HashMap::new();
        map.insert(NewportModel835PowerMeterRange::Twonanowatts, 0.004);
        map.insert(NewportModel835PowerMeterRange::Twentynanowatts, 0.004);
        map.insert(NewportModel835PowerMeterRange::Twohundrednanowatts, 0.002);
        map.insert(NewportModel835PowerMeterRange::Twomilliwatts, 0.0015);
        map.insert(NewportModel835PowerMeterRange::Twentymilliwatts, 0.001);
        map.insert(NewportModel835PowerMeterRange::Twohundredmilliwatts, 0.001);
        map
    };
}

// Define the possible ranges that can be displayed on the Newport 835 power meter. These are relevant for determining measurement uncertainty.
#[derive(Debug, Hash, Eq, PartialEq)]
pub enum NewportModel835PowerMeterRange {
    Twonanowatts,
    Twentynanowatts,
    Twohundrednanowatts,
    Twomilliwatts,
    Twentymilliwatts,
    Twohundredmilliwatts,
}

// Implement a method to 
impl NewportModel835PowerMeterRange {
    fn get_range(value: &f64) -> NewportModel835PowerMeterRange {
        // Find the range the power measurement is in
        match *value {
            x if x >= 0.0 && x <= 0.000000002 => NewportModel835PowerMeterRange::Twonanowatts,
            x if x > 0.000000002 && x <= 0.000000020 => NewportModel835PowerMeterRange::Twentynanowatts,
            x if x > 0.000000020 && x <= 0.000000200 => NewportModel835PowerMeterRange::Twohundrednanowatts,
            x if x > 0.000000200 && x <= 0.002 => NewportModel835PowerMeterRange::Twomilliwatts,
            x if x > 0.002 && x <= 0.020 => NewportModel835PowerMeterRange::Twentymilliwatts,
            x if x > 0.020 && x <= 0.200 => NewportModel835PowerMeterRange::Twohundredmilliwatts,
            _ => panic!("oops")
        }
        
    }
}

// Implement measurement for Newport 835 power meter measurements
impl Measurement<f64> for NewportModel835PowerMeterMeasurement {
    fn value(&self) -> f64 {
        self.value
    }
}

// Implement absolute uncertainty for newport model 835 power meter.
impl AbsoluteUncertainty<NewportModel835PowerMeterMeasurement, f64> for NewportModel835PowerMeterMeasurement {
    fn uncertainty(&self) -> f64 {
        // Determine the power reading scale we are working with
        let range = NewportModel835PowerMeterRange::get_range(&self.value);
        // Determine the associated fractional fullscaleuncertainty of this power scale.
        let fullscale_frac_uncertainty = *NEWPORT_MODEL_835_POWER_METER_FULLSCALE_UNCERTAINTIES.get(&range).unwrap();
        // Determine the associated reading fractional uncertainty of this power scale.
        let reading_frac_uncertainty = *NEWPORT_MODEL_835_POWER_METER_READING_UNCERTAINTIES.get(&range).unwrap();
        // Compute and return the absolute uncertainty
        self.value*(fullscale_frac_uncertainty + reading_frac_uncertainty)
    }
}