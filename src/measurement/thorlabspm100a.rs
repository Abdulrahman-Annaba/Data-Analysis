use crate::measurement::measurement::{AbsoluteUncertainty, Measurement};

const FRAC_UNCERTAINTY: f64 = 0.03;

pub struct ThorLabsPM100A_S120VC_PowerMeterMeasurement {
    value: f64
}

impl ThorLabsPM100A_S120VC_PowerMeterMeasurement {
    pub fn new(value: f64) -> ThorLabsPM100A_S120VC_PowerMeterMeasurement {
        ThorLabsPM100A_S120VC_PowerMeterMeasurement { value }
    }
}

impl Measurement<f64> for ThorLabsPM100A_S120VC_PowerMeterMeasurement {
    fn value(&self) -> f64 {
        self.value
    }
}

impl AbsoluteUncertainty<ThorLabsPM100A_S120VC_PowerMeterMeasurement, f64> for ThorLabsPM100A_S120VC_PowerMeterMeasurement {
    fn uncertainty(&self) -> f64 {
        // Please note: this is only correct if the measurement is within 440-980 nm
        self.value*FRAC_UNCERTAINTY
    }
}