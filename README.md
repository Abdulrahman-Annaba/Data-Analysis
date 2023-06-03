# TODO:

- Figure out how to actually use `pyo3` to build a python wheel from the `lib.rs`
- Implement computation methods on `Trial`
- Capture CLI input via python, as usual
- Handle creating trials on python side
- Call rust FFI from python side to do the actual data analysis
- Error check returned rust result on python side, report errors if any. Otherwise, continue.
- Plot data as requested
- Optionally save as svg (important)


# Rust FFI library structure
- measurement
    - power_meters
        - newport
            - (mod) tests
        - thorlabs
            - (mod) tests
    - power_measurements
        - (mod) traits
        - (mod) tests
- experiment
    - slide
        - (mod) tests
    - trial
        - `enum PowerMeterLabel`
        - `enum PolarizationState`
        - `struct Trial`
    - computation
        - implement `compute_efficiency_vs_mirror_angle` on `Trial`
        - implement `compute_efficiency_vs_incident_angle` on `Trial`
        - implement `compute_powers_vs_mirror_angle` on `Trial`
    - computation_tests

# Using PyO3

Looks like you have python interpret `struct`s as `class`es via the macro `#[pyclass]`