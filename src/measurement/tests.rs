use crate::measurement::{
    newportmodel835powermeter::NewportModel835PowerMeterMeasurement,
    power_measurement::{AbsoluteUncertainty, Measurement},
    thorlabspm100a::ThorLabsPM100A_S120VC_PowerMeterMeasurement,
};
#[test]
fn test_newport_measurement() {
    // Measurement in watts
    let measurement = 0.001;
    // convert this into a newport measurement
    let newport_measurement = NewportModel835PowerMeterMeasurement::new(measurement);
    // Test value
    assert_eq!(&measurement, newport_measurement.value());
    // Test uncertainty according to specification
    let reading_frac_uncertainty = 0.0015;
    let fullscale_frac_uncertainty = 0.0005;
    let correct_measurement_uncertainty =
        measurement * (reading_frac_uncertainty + fullscale_frac_uncertainty);
    assert_eq!(
        correct_measurement_uncertainty,
        newport_measurement.uncertainty()
    );
}

#[test]
fn test_thorlabs_pm100a_s120vc_measurement() {
    // Measurement in watts
    let measurement = 0.01;
    // Convert this into a thorlabs measurement
    let thorlabs_measurement = ThorLabsPM100A_S120VC_PowerMeterMeasurement::new(measurement, 637.8);
    // Test value
    assert_eq!(&measurement, thorlabs_measurement.value());
    // Test uncertainty according to specification
    let frac_uncertainty = 0.03;
    let correct_measurement_uncertainty = measurement * frac_uncertainty;
    assert_eq!(
        correct_measurement_uncertainty,
        thorlabs_measurement.uncertainty()
    );
}
