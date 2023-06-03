use crate::experiment::slide::Slide;
use crate::measurement::power_measurement::traits::{ArithmeticOps, Background};
use ndarray::Array2;

/// Represents a trial
pub struct Trial<BackgroundT, BackgroundR, NumberType>
where
    BackgroundT: Background<NumberType>,
    BackgroundR: Background<NumberType>,
    NumberType: ArithmeticOps,
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
    slide: Slide<NumberType>,
}

/// An enumeration over the allowed polarization states for light in this experiment.
pub enum PolarizationState {
    Horizontal,
    Vertical,
}
/// An enumeration of the two possible power meter labels in the experiment
pub enum PowerMeterLabel {
    SensorA,
    SensorC,
}

impl PowerMeterLabel {
    /// Returns an integer corresponding to the row index
    pub fn get_computation_parameters_row_index(&self) -> u8 {
        match self {
            Self::SensorA => 0,
            Self::SensorC => 1,
        }
    }
}

/// The result of a computation. May have an associated error related to the error in the dependent variable.
/// In addition, it must have a computation type which informs the receiver what is being computed.
pub struct ComputationResult<T> {
    value: T,
    associated_error: Option<T>,
    computation_type: ComputationType,
}

/// Represents the different possible types of computations available in a trial.
pub enum ComputationType {
    EfficiencyVsMirrorAngle,
    EfficiencyVsIncidentAngle,
    PowerVsMirrorAngle,
}
