// Defines the interface for measurements
pub trait Measurement<T> {
    // All measurements should at least have a value
    fn value(&self) -> T;
}

// Define an absolute uncertainty inferface.
// It should be generic for any type that implements Measurement.
pub trait AbsoluteUncertainty<M: Measurement<T>, T> {
    // An absolute uncertainty.
    fn uncertainty(&self) -> T;
}