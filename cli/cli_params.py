from dataclasses import dataclass
from typing import Tuple
from pathlib import Path
import numpy as np


@dataclass
class CliParams:
    """Data class to contain the CliParameters"""
    trials: Tuple[Tuple[Path, str]]
    """The locations and names for the trials"""
    incident_angles: np.ndarray
    """The incident angles to plot at"""
    plot_incident_angle_plot: bool
    """Whether or not ot plot Total efficiency vs. incident angle"""
    # plot_mirror_angle_plot: bool
    # """Whether or not to plot efficiency vs. mirror angle"""
    # plot_power_plot: bool
    # """Whether or not to plot power vs. mirror angle"""
    error: bool
    """Whether or not to include error bars"""
    # power_plot_scale: float
    # """The factor to multiply power measurements in the power vs. mirror angle plot"""
    show_figures: bool
    """Whether or not to show figures"""
    save_figures: bool
    """Whether or not to save figures"""
    reuse_figures: bool
    """Whether or not to reuse figures of the same axes"""
    theory: bool
    """Whether or not to plot theoretical values"""
    title: str
    """The title to set for the figures"""
