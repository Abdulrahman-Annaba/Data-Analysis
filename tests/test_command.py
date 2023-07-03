import cli.commands as cmds
from cli.cli_params import CliParams
from pathlib import Path
import numpy as np
from data_analysis.data_extraction import extract_trial_info, extract_grating_info


def test_plot_data_command():
    # Make CLI params
    params = CliParams(
        trials=((Path("../Trials/GR13-1205 (UP) (5)"), "Left, P"),),
        incident_angles=None,
        plot_incident_angle_plot=True,
        error=True,
        show_figures=True,
        save_figures=False,
        reuse_figures=True,
        theory=True,
        title=None  # type:ignore
    )
    # Make receiver
    plot_gen = cmds.PlotGenerator(params)
    # Make invoker
    invoker = cmds.Invoker()
    # make trial and compute data
    trial = extract_trial_info(Path("../Trials/GR13-1205 (UP) (5)"))
    grating = extract_grating_info(Path("../Trials/GR13-1205 (UP) (5)"))
    spr_angles = grating.spr_angles(10)
    woods = grating.woods_anomaly_angles(10)
    error = trial.compute_efficiency_error_vs_incident_angle(
        params.incident_angles)
    data = trial.compute_efficiency_vs_incident_angle(params.incident_angles)
    # make command to plot data
    cmd = cmds.PlotTotalEfficiencyCommand(
        plot_gen, data, params.trials[0][1], params.title, error, spr_angles, woods)
    invoker.add_command(cmd)
    invoker.add_command(cmds.ShowFigures(plot_gen))
    # Execute command
    invoker.execute_all_commands()


def test_reuse_figure():
    """Tests whether or not we can reuse figures properly"""
    # Initialize params
    trials = ((Path("../Trials/GR13-1205 (UP) (6)"), "S Polarization"),
              (Path("../Trials/GR13-1205 (UP) (5)"), "P Polarization"))
    params = CliParams(
        trials,  # type: ignore
        incident_angles=None,  # type: ignore
        plot_incident_angle_plot=True,
        error=True,
        show_figures=True,
        reuse_figures=True,
        save_figures=False,
        theory=True,
        title="GR13-1205, Wavelength = 637.8 nm"
    )
    plot_gen = cmds.PlotGenerator(params)
    # Get first figure
    fig1 = plot_gen._get_fig("Total Efficiency vs. Incident Angle")
    # Get same fig
    fig2 = plot_gen._get_fig("Total Efficiency vs. Incident Angle")
    # Should be the same
    assert fig1 == fig2
