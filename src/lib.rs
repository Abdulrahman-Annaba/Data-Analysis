use pyo3::{pymodule, types::PyModule, PyResult, Python};

mod cli;
mod experiment;
mod measurement;

/// A Rust module to handle the messy details of extracting data from trial folders and computing said data.
#[pymodule]
fn data_analysis(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    // m.add_function(wrap_pyfunction!(fun, m)?)?;
    todo!()
}
