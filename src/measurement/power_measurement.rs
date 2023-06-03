/// Common traits found across the program
pub mod traits {
    use crate::experiment::trial::PolarizationState;
    use crate::experiment::trial::PowerMeterLabel;
    /// A trait which introduces the concept of a measurement.
    pub trait Measurement<T: ArithmeticOps> {
        /// Returns the value of a measurement
        fn value(&self) -> T;
    }

    /// A trait which introduces the concept of an absolute uncertainty. Implementors must also implement the `Measurement<T: ArithmeticOps>` trait
    pub trait AbsoluteUncertainty<T: ArithmeticOps>: Measurement<T> {
        // An absolute uncertainty.
        fn uncertainty(&self) -> T;
    }

    /// A trait which introduces the concept of a background power measurement.
    pub trait Background<T: ArithmeticOps> {
        // Get the background power reading
        fn background(&self) -> T;
    }

    use std::ops::{Add, Div, Mul, Sub};

    /// Essentially a wrapper trait around the four basic arithmetic operations. This makes the code easier to read in other places of the program.
    pub trait ArithmeticOps:
        Add<Output = Self> + Sub<Output = Self> + Mul<Output = Self> + Div<Output = Self>
    where
        Self: std::marker::Sized,
    {
    }

    /// The power of Rust's rich type system. Here, I implement my created trait above automatically for any type that satisfies the four basic arithmetic operations.
    impl<T> ArithmeticOps for T where
        T: Add<Output = T> + Sub<Output = T> + Mul<Output = T> + Div<Output = T>
    {
    }

    pub trait IncidentPower<V: ArithmeticOps> {
        // Should have a method called compute which takes an immutable reference to itself and computes a value
        // This should accept any two measurements types and return the appropriate value.
        fn compute_incident_power<R, Br, T, Tr>(
            &self,
            reflected_power: &R,
            reflected_power_background: &Br,
            reflected_power_meter_label: &PowerMeterLabel,
            transmitted_power: &T,
            transmitted_power_background: &Tr,
            transmitted_power_meter_label: &PowerMeterLabel,
            polarization: &PolarizationState,
        ) -> V
        where
            R: Measurement<V>,
            Br: Background<V>,
            Tr: Background<V>,
            T: Measurement<V>;
    }

    /// Define the Efficiency interface
    pub trait Efficiency<V: ArithmeticOps> {
        fn compute_efficiency<R, Br, T, Tr>(
            &self,
            reflected_power: &R,
            reflected_power_background: &Br,
            reflected_power_meter_label: &PowerMeterLabel,
            transmitted_power: &T,
            transmitted_power_background: &Tr,
            transmitted_power_meter_label: &PowerMeterLabel,
            polarization: &PolarizationState,
        ) -> V
        where
            R: Measurement<V>,
            Br: Background<V>,
            Tr: Background<V>,
            T: Measurement<V>;
    }
}
