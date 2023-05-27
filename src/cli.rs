use std::path::PathBuf;

// def main(
//     trial: Tuple[Tuple[Path, str]],
//     grating_angle: Tuple[float],
//     grating_plot: bool,
//     mirror_plot: bool,
//     power_plot: bool,
//     scale: float,
//     show_figure: bool,
//     save_figure: bool,
//     reuse_figure: bool,
//     theory: bool,
//     title: str
// ):
struct Cli {
    trials: Vec<(PathBuf, String)>,
    grating_angles: Vec<f64>,
    grating_plot: bool,
    mirror_plot: bool,
    power_plot: bool,
    scale: f64,
    show_figure: bool,
    save_figure: bool,
    reuse_figure: bool,
    theory: bool,
    title: String,
}

// Make From implementation for python class that stores the CLI args that are produced in plotdata.py
