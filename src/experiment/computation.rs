use std::collections::HashSet;

use polars::export::ahash::HashMap;

use crate::{
    experiment::trial::Trial,
    measurement::power_measurement::traits::{ArithmeticOps, Background},
};

// Implement some functions for a trial which uses f64 number types
impl<BackgroundT, BackgroundR> Trial<BackgroundT, BackgroundR, f64>
where
    BackgroundT: Background<f64>,
    BackgroundR: Background<f64>,
{
    /// Computes the efficiency vs mirror angle for the given incident angles. The provided incident angles must be explicitly present in the data.
    pub fn compute_efficiency_vs_mirror_angle(
        &mut self,
        incident_angles: HashSet<f64>,
    ) -> HashMap<f64, ndarray::Array2<f64>> {
        todo!()
    }

    /// Computes the efficiency vs incident angle for the given incident angles. The provided incident angles must be explicitly present in the data.
    pub fn compute_efficiency_vs_incident_angle(
        &mut self,
        incident_angles: HashSet<f64>,
    ) -> ndarray::Array2<f64> {
        todo!()
    }

    /// Computes the one-sided error in the efficiencies vs incident angles. The provided incident angles must be explicitly present in the data.
    pub fn compute_efficiency_vs_incident_angle_error(
        &mut self,
        incident_angles: HashSet<f64>,
    ) -> ndarray::Array2<f64> {
        todo!()
    }

    /// Computes the powers vs mirror angle for the given incident angles. The provided incident angles must be explicitly present in the data.
    pub fn compute_power_vs_mirror_angle(
        &mut self,
        incident_angles: HashSet<f64>,
    ) -> HashMap<f64, ndarray::Array2<f64>> {
        todo!()
    }
}
