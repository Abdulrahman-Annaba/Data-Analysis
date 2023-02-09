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
    help="A 2-tuple, consisting of Trial folder path and desired trial label. Required. You can pass this option multiple times to plot multiple trials."
)
@click.option(
    '-g', '--grating-angle',
    nargs=1,
    type=click.FLOAT,
    multiple=True,
    help="The grating angle to include in the plots. By default, it includes all the angles found in the dataset. Add the flag multiple times to add each grating angle of interest."
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
def main(
    trial: Union[Tuple[Tuple[Path, str]], Tuple[Path, str]],
    grating_angles: Union[List[float], float],
    scale: float,
    show_figure: bool,
    save_figure: bool,
    reuse_figure: bool
):
    """
    Extract, analyze, and plot diffraction grating trials.
    """

    # TODO: make this code less repetitive (if it matters)


    # If we have multiple trials
    if type(trial) == tuple:

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
        # TODO: Fix bug where some trials are not being plotted (Perhaps error with storing via hashmap?)
        for ind_trial in trial:
            # Get the trial folder path and the trial label
            (trial_folder, trial_label) = ind_trial
            # Check if trial_folder is an existing directory
            if trial_folder.exists() and trial_folder.is_dir():
                # Create the trial instance. TODO: add custom optional option to specify how to compute incident power and efficiency.
                trial_instance = data_analysis.data_extraction.extract_trial_info(
                    trial_folder,
                    data_analysis.data_computation.default_incident_power,
                    data_analysis.data_computation.default_efficiency,
                    trial_name=trial_label
                )
                # Compute the powers vs mirror angles data
                power_vs_mirror_angle = trial_instance.compute_powers_vs_mirror_angle(grating_angles, power_scale_factor=scale)
                # Compute the efficiency vs mirror angle data
                efficiency_vs_mirror_angle = trial_instance.compute_efficiency_vs_mirror_angle(grating_angles)
                # Compute the efficiency vs grating angle data
                efficiency_vs_grating_angle = trial_instance.compute_efficiency_vs_grating_angle(grating_angles)
                # If we don't want to reuse the figures for the given trials, get the next valid figure number for each plot and plot.
                if not reuse_figure:
                    data_analysis.data_plotting.plot_powers_vs_mirror_angle(power_vs_mirror_angle, next(power_vs_mirror_angle_figure))
                    data_analysis.data_plotting.plot_efficiency_vs_mirror_angle(efficiency_vs_mirror_angle, next(efficiency_vs_mirror_angle_figure))
                    data_analysis.data_plotting.plot_efficiency_vs_grating_angle(efficiency_vs_grating_angle, next(efficiency_vs_grating_angle_figure), label=trial_instance.trial_label)
                else:
                    # Just plot the data on the same figure
                    data_analysis.data_plotting.plot_powers_vs_mirror_angle(power_vs_mirror_angle, power_vs_mirror_angle_figure)
                    data_analysis.data_plotting.plot_efficiency_vs_mirror_angle(efficiency_vs_mirror_angle, efficiency_vs_mirror_angle_figure)
                    data_analysis.data_plotting.plot_efficiency_vs_grating_angle(efficiency_vs_grating_angle, efficiency_vs_grating_angle_figure, label=trial_instance.trial_label)

        # Show the figures, if requested.
        if show_figure:
            plt.show()
        # Save the figures, if requested. TODO: Check if this properly saves *all* the figures or just the currently selected figure in pyplot
        if save_figure:
            plt.savefig()
    # If we have only one trial
    else:
        # Get the trial folder path and the trial label
        (trial_folder, trial_label) = trial
        # Initialize figure numbers
        (power_vs_mirror_angle_figure, efficiency_vs_mirror_angle_figure, efficiency_vs_grating_angle_figure) = (1, 2, 3)
        # Check if trial_folder is an existing directory
        if trial_folder.exists() and trial_folder.is_dir():
            # Create the trial instance. TODO: add custom optional option to specify how to compute incident power and efficiency.
            trial_instance = data_analysis.data_extraction.extract_trial_info(
                trial_folder,
                data_analysis.data_computation.default_incident_power,
                data_analysis.data_computation.default_efficiency,
                trial_name=trial_label
            )
            # Compute the powers vs mirror angles data
            power_vs_mirror_angle = trial_instance.compute_powers_vs_mirror_angle(grating_angles, power_scale_factor=scale)
            # Compute the efficiency vs mirror angle data
            efficiency_vs_mirror_angle = trial_instance.compute_efficiency_vs_mirror_angle(grating_angles)
            # Compute the efficiency vs grating angle data
            efficiency_vs_grating_angle = trial_instance.compute_efficiency_vs_grating_angle(grating_angles)
            # Plot the data
            data_analysis.data_plotting.plot_powers_vs_mirror_angle(power_vs_mirror_angle, power_vs_mirror_angle_figure)
            data_analysis.data_plotting.plot_efficiency_vs_mirror_angle(efficiency_vs_mirror_angle, efficiency_vs_mirror_angle_figure)
            data_analysis.data_plotting.plot_efficiency_vs_grating_angle(efficiency_vs_grating_angle, efficiency_vs_grating_angle_figure, label=trial_instance.trial_label)
            # Show the figures, if requested.
            if show_figure:
                plt.show()
            # Save the figures, if requested. TODO: Check if this properly saves *all* the figures or just the currently selected figure in pyplot
            if save_figure:
                plt.savefig()
