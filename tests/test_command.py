import cli.commands as cmds
from cli.cli_params import CliParams
from pathlib import Path
import numpy as np
from data_analysis.data_extraction import extract_trial_info, extract_grating_info


def test_plot_data_command():
    # Make CLI params
    params = CliParams(
        trials=((Path("../Trials/GR13-1205 (UP) (5)"), "Left, P"),),
        incident_angles=np.array([], dtype=np.float64),
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
