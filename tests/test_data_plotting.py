import data_analysis.data_plotting as plotmod
import data_analysis.data_extraction as extr
import matplotlib.pyplot as plt
from pathlib import Path


def test_plot_total_eff_vs_incident_angle():
    trial = extr.extract_trial_info(Path("../Trials/GR13-1205 (UP) (5)"))
    grating = extr.extract_grating_info(Path("../Trials/GR13-1205 (UP) (5)"))

    plotmod.plot_efficiency_vs_incident_angle(trial.compute_efficiency_vs_incident_angle(
    ), 0, trial.trial_label, "test plot", trial.compute_efficiency_error_vs_incident_angle(), grating.spr_angles(10), grating.woods_anomaly_angles(10))
