"""CLI portion of the plotting program."""

# Import some useful things, like type hints, Path objects, click (package for creating CLIs easily), and pyplot (just to save or show plots at the end.)
from typing import List, Union, Tuple
from pathlib import Path
import click
import matplotlib.pyplot as plt
from dataclasses import dataclass

# Import modules from the data analysis module
import data_analysis.data_computation
import data_analysis.data_extraction
import data_analysis.data_plotting
import data_analysis.theory as theoretical
from cli.commands import *
from cli.cli_params import CliParams

# TODO: Implement commented features


@click.command()
@click.option(
    '-t', '--trial',
    multiple=True,
    required=True,
    type=(click.Path(exists=True, dir_okay=True,
          readable=True, path_type=Path), str),
    help="A 2-tuple, consisting of Trial folder path and desired trial label. You can pass this option multiple times to plot multiple trials. Trial folder must contain a data.csv file and a computation_parameters.csv file. Example formatting for these files is available at https://github.com/Abdulrahman-Annaba/Data-Analysis."
)
@click.option(
    '-i', '--incident-angle',
    nargs=1,
    type=click.FLOAT,
    multiple=True,
    default=None,
    help="The incident angle to include in the plots. By default, it includes all the angles found in a dataset. Specify the flag multiple times to add each incident angle of interest."
)
@click.option(
    '--incident-angle-plot/--no-incident-angle-plot',
    default=True,
    type=click.BOOL,
    help="Whether or not to include Efficiency vs. Incident Angle plots. Default True."
)
# @click.option(
#     '--mirror-angle-plot/--no-mirror-angle-plot',
#     default=False,
#     type=click.BOOL,
#     help="Whether or not to include Efficiency vs. Mirror Angle plots. Default False."
# )
# @click.option(
#     '--power-plot/--no-power-plot',
#     default=False,
#     type=click.BOOL,
#     help="Whether or not to include Power vs. Mirror Angle plots. Default False."
# )
@click.option(
    '-e/-ne', '--error/--no-error',
    default=True,
    type=click.BOOL,
    help="Whether or not to include error bars. Defaults to True."
)
# @click.option(
#     '-m', '--scale',
#     default=1,
#     type=click.FLOAT,
#     help="Number to scale power readings on the power vs mirror angle figure. Default 1 (no scaling)."
# )
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
    '-th/-nth', '--theory/--no-theory',
    default=False,
    type=click.BOOL,
    help="Whether or not to include theoretical predictions for the locations of SPR. Default False."
)
@click.option(
    '--title',
    default=None,
    type=click.STRING,
    help="Title to use for graphs. If left blank, defaults to respective plot title."
)
def main(
    trial: Tuple[Tuple[Path, str]],
    incident_angle: Tuple[float],  # type: ignore
    incident_angle_plot: bool,
    # mirror_angle_plot: bool,
    # power_plot: bool,
    error: bool,
    # scale: float,
    show_figure: bool,
    save_figure: bool,
    reuse_figure: bool,
    theory: bool,
    title: str
):
    """
    Extract, analyze, and plot diffraction grating trials.

    Example usage:

    python main.py --show-figure --reuse-figure --scale 1000000 -t path/to/trial_1_folder "1st Trial" -t path/to/trial_2_folder "2nd Trial" -i -50 -i 0 -i 50
    """
    # At the moment, only incident angle plots are functional.
    # TODO: Finish features involving power plot and mirror angle plot

    # If we have multiple grating angles, return the unique ones and sort them. If it's None (the default), just pass

    if incident_angle is None:
        pass
    else:
        incident_angle = list(set(incident_angle))  # type: ignore
        incident_angle.sort()
        incident_angle = tuple(incident_angle)  # type: ignore
    # If we have multiple trials, return the ones that are unique: ie, no repeating trial folder AND name
    if len(trial) > 1:
        trial = tuple(set(trial))

    incident_angle: np.ndarray = np.array(incident_angle)
    # Make the CLI parameters dataclass
    # params = CliParams(trials=trial, incident_angles=incident_angle,
    #                    plot_incident_angle_plot=incident_angle_plot, plot_mirror_angle_plot=mirror_angle_plot, plot_power_plot=power_plot, power_plot_scale=scale, show_figures=show_figure, save_figures=save_figure, reuse_figures=reuse_figure, theory=theory, title=title, error=error)

    # Make the CLI parameters dataclass
    params = CliParams(trials=trial, incident_angles=incident_angle,
                       plot_incident_angle_plot=incident_angle_plot, error=error, show_figures=show_figure, save_figures=save_figure, theory=theory, title=title, reuse_figures=reuse_figure)
    # Make the PlotGenerator object to handle making the plots
    plot_maker = PlotGenerator(params)
    # Make the Invoker which keeps track of the requested commands
    invoker = Invoker()
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
        else:
            raise Exception(f"{ind_trial} is not a directory that exists.")
        # If we want theoretical values, initialize the theoretical gratings.
        # TODO: Make this work for all trials, not just the first one.
        if theory:
            grating = data_analysis.data_extraction.extract_grating_info(
                trial_folder)
            # Hard code this to up to 10 orders because that should be enough
            spr_angles = grating.spr_angles(10)
            woods = grating.woods_anomaly_angles(10)
        # if params.plot_power_plot:
        #     # Compute the powers vs mirror angles data
        #     power_vs_mirror_angle = trial_instance.compute_powers_vs_mirror_angle(
        #         incident_angles_to_use=incident_angle, power_scale_factor=scale)
        #     command = PlotPowerCommand(
        #         plot_maker, power_vs_mirror_angle, trial_instance.trial_label)
        #     invoker.add_command(command)
        # if params.plot_mirror_angle_plot:
        #     # Compute the efficiency vs mirror angle data
        #     efficiency_vs_mirror_angle = trial_instance.compute_efficiency_vs_mirror_angle(
        #         incident_angles_to_use=incident_angle)
        #     command = PlotEfficiencyCommand(
        #         plot_maker, efficiency_vs_mirror_angle, trial_instance.trial_label)
        #     invoker.add_command(command)
        if params.plot_incident_angle_plot:
            # Compute the efficiency vs incident angle data
            efficiency_vs_incident_angle = trial_instance.compute_efficiency_vs_incident_angle(
                incident_angles_to_use=incident_angle)
            # Compute error if requested
            if params.error:
                eff_err_vs_incident_angle = trial_instance.compute_efficiency_error_vs_incident_angle(
                    incident_angles_to_use=incident_angle)
            else:
                eff_err_vs_incident_angle = None
            # Make the command to plot the efficiency
            command = PlotTotalEfficiencyCommand(
                plot_maker, efficiency_vs_incident_angle, trial_instance.trial_label, params.title, eff_err_vs_incident_angle, spr_angles, woods  # type: ignore
            )
            # Add the command
            invoker.add_command(command)
    if params.show_figures:
        invoker.add_command(ShowFigures(plot_maker))
    # Execute the commands, in order
    invoker.execute_all_commands()

    # # If we don't want to reuse the figures for the given trials, get the next valid figure number for each plot and plot.
    # if not reuse_figure:
    #     if power_plot:
    #         data_analysis.data_plotting.plot_powers_vs_mirror_angle(power_vs_mirror_angle, next(
    #             power_vs_mirror_angle_figure), label_prefix=f"{trial_instance.trial_label}: ")
    #     if mirror_plot:
    #         data_analysis.data_plotting.plot_efficiency_vs_mirror_angle(efficiency_vs_mirror_angle, next(
    #             efficiency_vs_mirror_angle_figure), label_prefix=f"{trial_instance.trial_label}: ")
    #     if grating_plot:
    #         if theory:
    #             data_analysis.data_plotting.plot_efficiency_vs_incident_angle(efficiency_vs_incident_angle, next(
    #                 efficiency_vs_incident_angle_figure), label=trial_instance.trial_label, spr_angles=spr_angles, woods=woods, title=title)
    #         else:
    #             data_analysis.data_plotting.plot_efficiency_vs_incident_angle(efficiency_vs_incident_angle, next(
    #                 efficiency_vs_incident_angle_figure), label=trial_instance.trial_label, title=title)
    # else:
    #     # Just plot the data on the same figure
    #     if power_plot:
    #         data_analysis.data_plotting.plot_powers_vs_mirror_angle(
    #             power_vs_mirror_angle, power_vs_mirror_angle_figure, label_prefix=f"{trial_instance.trial_label}: ")
    #     if mirror_plot:
    #         data_analysis.data_plotting.plot_efficiency_vs_mirror_angle(
    #             efficiency_vs_mirror_angle, efficiency_vs_mirror_angle_figure, label_prefix=f"{trial_instance.trial_label}: ")
    #     if grating_plot:
    #         if theory:
    #             data_analysis.data_plotting.plot_efficiency_vs_incident_angle(
    #                 efficiency_vs_incident_angle, efficiency_vs_incident_angle_figure, label=trial_instance.trial_label, spr_angles=spr_angles, woods=woods, title=title)
    #         else:
    #             data_analysis.data_plotting.plot_efficiency_vs_incident_angle(
    #                 efficiency_vs_incident_angle, efficiency_vs_incident_angle_figure, label=trial_instance.trial_label, title=title)
    # # To prevent multiple plots of the theoretical values
    # theory = False
