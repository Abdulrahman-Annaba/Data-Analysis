// Defines the interface for measurements
pub trait Measurement<T> {
    // All measurements should at least have a value
    fn value(&self) -> &T;
}

// Define an absolute uncertainty inferface.
// This takes a generic type parameter T. In addition, it also requires that the implementor also implement Measurement<T>
pub trait AbsoluteUncertainty<T>: Measurement<T> {
    // An absolute uncertainty.
    fn uncertainty(&self) -> T;
}

// Define a background measurement interface.
// This takes a generic type parameter T. In addition, it also requires that the implementor also implement Measurement<T>
pub trait Background<T> {
    // Get the background power reading
    fn background(&self) -> &T;
}

/// An enumeration of the two possible power meter labels in the experiment
pub enum PowerMeterLabel {
    SensorA,
    SensorC,
}
