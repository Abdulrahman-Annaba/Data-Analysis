"""CLI portion of the plotting program."""

# Import some useful things, like type hints, Path objects, click (package for creating CLIs easily), and pyplot (just to save or show plots at the end.)
from typing import List, Union, Tuple
from pathlib import Path
import click
import matplotlib.pyplot as plt

# Import modules from the data analysis module
import data_analysis.data_computation, data_analysis.data_extraction, data_analysis.data_plotting

# Define a CLI command, and the valid options. Most of these are self-explanatory. For every option, there is an associated parameter in the actual function below.
@click.command()
@click.option(
    '-t', '--trial',
    multiple=True,
    required=True,
    type=(click.Path(exists=True, dir_okay=True, readable=True, path_type=Path), str),
    help="A 2-tuple, consisting of Trial folder path and desired trial label. You can pass this option multiple times to plot multiple trials. Trial folder must contain a data.csv file and a computation_parameters.csv file. Example formatting for these files is available at https://github.com/Abdulrahman-Annaba/Data-Analysis."
)
@click.option(
    '-g', '--grating-angle',
    nargs=1,
    type=click.FLOAT,
    multiple=True,
    help="The grating angle to include in the plots. By default, it includes all the angles found in the dataset. Add the flag multiple times to add each grating angle of interest."
)
@click.option(
    '--grating-plot/--no-grating-plot',
    default=True,
    type=click.BOOL,
    help="Whether or not to include Efficiency vs. Grating Angle plots. Default True."
)
@click.option(
    '--mirror-plot/--no-mirror-plot',
    default=False,
    type=click.BOOL,
    help="Whether or not to include Efficiency vs. Mirror Angle plots. Default False."
)
@click.option(
    '--power-plot/--no-power-plot',
    default=False,
    type=click.BOOL,
    help="Whether or not to include Efficiency vs. Grating Angle plots. Default False."
)
@click.option(
    '-m', '--scale',
    default=1,
    type=click.FLOAT,
    help="Number to scale power readings on the power vs mirror angle figure. Default 1 (no scaling)."
)
@click.option(
    '-s/-ns', '--show-figure/--no-show-figure',
    default=True,
    type=click.BOOL,
    help="Whether or not to display figures. Default True."
)
@click.option(
    '-sv/-nsv', '--save-figure/--no-save-figure',
    default=False,
    type=click.BOOL,
    help="Whether or not to save the plots in the current working directory. Default False."
)
@click.option(
    '-r/-nr', '--reuse-figure/--no-reuse-figure',
    default=True,
    type=click.BOOL,
    help="Whether or not to plot multiple trials to the same figures or to reuse figures. Default True."
)
@click.option(
    '-d/-nd', '--print-data/--no-print-data',
    default=False,
    type=click.BOOL,
    help="Whether or not to print data to standard output. Default False."
)
def main(
    trial: Tuple[Tuple[Path, str]],
    grating_angle: Tuple[float],
    grating_plot: bool,
    mirror_plot: bool,
    power_plot: bool,
    scale: float,
    show_figure: bool,
    save_figure: bool,
    reuse_figure: bool,
    print_data: bool,
):
    """
    Extract, analyze, and plot diffraction grating trials.

    Example usage:

    python main.py --show-figure --reuse-figure --scale 1000000 -t path/to/trial_1_folder "1st Trial" -t path/to/trial_2_folder "2nd Trial" -g -50 -g 0 -g 50
    """

    # If we have multiple grating angles, return the unique ones and sort them
    grating_angle_absent = False
    if len(grating_angle) > 0:
        grating_angle = list(set(grating_angle))
        grating_angle.sort()
        grating_angle = tuple(grating_angle)
    # If no grating angles were passed in, switch a flag
    else:
        grating_angle_absent = True
    # If we have multiple trials, return the ones that are unique: ie, no repeating trial folder AND name
    if len(trial) > 1:
        trial = tuple(set(trial))
    
    # If we want to reuse the figures
    if reuse_figure:
        (power_vs_mirror_angle_figure, efficiency_vs_mirror_angle_figure, efficiency_vs_grating_angle_figure) = (0, 1, 2)
    # If we're going to make unique figures for each trial
    else:
        # compute number of figures needed
        number_of_figures = len(trial)*3
        # specify figure numbers for each type of plot
        power_vs_mirror_angle_figure = iter(range(0, int(number_of_figures/3)))
        efficiency_vs_mirror_angle_figure = iter(range(int(number_of_figures/3), int(2*number_of_figures/3)))
        efficiency_vs_grating_angle_figure = iter(range(int(2*number_of_figures/3), int(number_of_figures)))
    
    # Loop over the trials provided
    for ind_trial in trial:
        # Get the trial folder path and the trial label
        (trial_folder, trial_label) = ind_trial
        if trial_folder.exists() and trial_folder.is_dir():
            # Create the trial instance. TODO: add custom optional option to specify how to compute incident power and efficiency.
            trial_instance = data_analysis.data_extraction.extract_trial_info(
                trial_folder,
                trial_name=trial_label
            )
            # Compute the powers vs mirror angles data
            power_vs_mirror_angle = trial_instance.compute_powers_vs_mirror_angle(grating_angles_to_use=grating_angle, power_scale_factor=scale)
            # Compute the efficiency vs mirror angle data
            efficiency_vs_mirror_angle = trial_instance.compute_efficiency_vs_mirror_angle(grating_angles_to_use=grating_angle)
            # Compute the efficiency vs grating angle data
            efficiency_vs_grating_angle = trial_instance.compute_efficiency_vs_grating_angle(grating_angles_to_use=grating_angle)
            if print_data:
                print(trial_label, power_vs_mirror_angle)
                print(trial_label, efficiency_vs_mirror_angle)
                print(trial_label, efficiency_vs_grating_angle)
            # If we don't want to reuse the figures for the given trials, get the next valid figure number for each plot and plot.
            if not reuse_figure:
                if power_plot:
                    data_analysis.data_plotting.plot_powers_vs_mirror_angle(power_vs_mirror_angle, next(power_vs_mirror_angle_figure), label_prefix=f"{trial_instance.trial_label}: ")
                if mirror_plot:
                    data_analysis.data_plotting.plot_efficiency_vs_mirror_angle(efficiency_vs_mirror_angle, next(efficiency_vs_mirror_angle_figure), label_prefix=f"{trial_instance.trial_label}: ")
                if grating_plot:
                    data_analysis.data_plotting.plot_efficiency_vs_grating_angle(efficiency_vs_grating_angle, next(efficiency_vs_grating_angle_figure), label=trial_instance.trial_label)
            else:
                # Just plot the data on the same figure
                if power_plot:
                    data_analysis.data_plotting.plot_powers_vs_mirror_angle(power_vs_mirror_angle, power_vs_mirror_angle_figure, label_prefix=f"{trial_instance.trial_label}: ")
                if mirror_plot:
                    data_analysis.data_plotting.plot_efficiency_vs_mirror_angle(efficiency_vs_mirror_angle, efficiency_vs_mirror_angle_figure, label_prefix=f"{trial_instance.trial_label}: ")
                if grating_plot:
                    data_analysis.data_plotting.plot_efficiency_vs_grating_angle(efficiency_vs_grating_angle, efficiency_vs_grating_angle_figure, label=trial_instance.trial_label)

    # Show the figures, if requested.
    if show_figure:
        plt.show()
    # Save the figures, if requested. TODO: Check if this properly saves *all* the figures or just the currently selected figure in pyplot
    if save_figure:
        plt.savefig()
