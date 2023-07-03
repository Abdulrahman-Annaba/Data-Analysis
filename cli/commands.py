"""Module to define commands for plotting"""
import matplotlib.pyplot as plt
from cli.command_definition import Command
from typing import Dict, List
import numpy as np
from cli.cli_params import CliParams
from data_analysis.data_plotting import *

# TODO: Finish implementing power and mirror angle plot commands


class Invoker:
    """Class the stores commands and executes them"""
    commands: List[Command]

    def __init__(self) -> None:
        self.commands = []

    def add_command(self, command: Command):
        self.commands.append(command)

    def execute_all_commands(self):
        for command in self.commands:
            command.execute()


class PlotGenerator:
    """Receiver class that handles the business logic of generating figures"""

    def __init__(self, cli_params: CliParams):
        self.params = cli_params

    def plot_total_efficiency(self, data: np.ndarray, trial_label: str, title: str = None, error: np.ndarray = None, spr_angles: Dict[int, float] = None, woods: Dict[int, float] = None  # type: ignore
                              ):
        """Handles the business logic of plotting and saving the total efficiency vs incident angles"""
        fig_number = self._get_fig(
            "Total Efficiency vs. Incident Angle")

        plot_efficiency_vs_incident_angle(
            data, fig_number, series_label=trial_label, spr_angles=spr_angles, woods=woods, title=title, error=error)
        if self.params.save_figures:
            plt.figure(fig_number)
            plt.savefig(trial_label, format="svg")

    def showfigures(self):
        """Shows all figures"""
        plt.show()

    # def plot_efficiency(self, data: Dict[float, np.ndarray], trial_label: str):
    #     """Handles the business logic of plotting and saving the efficiency vs mirror angle"""
    #     fig_number = self._get_fig("Efficiency vs. Mirror Angle")
    #     plot_efficiency_vs_mirror_angle(data, fig_number)
    #     if self.params.save_figures:
    #         plt.figure(fig_number)
    #         plt.savefig(trial_label, format="svg")

    # def plot_powers(self, data: Dict[float, np.ndarray], trial_label: str):
    #     """Handles the business logic of plotting and saving the powers vs mirror angles"""
    #     fig_number = self._get_fig("Power vs. Mirror Angle")
    #     plot_powers_vs_mirror_angle(data, fig_number)
    #     if self.params.save_figures:
    #         plt.figure(fig_number)
    #         plt.savefig(trial_label, format="svg")

    def _get_fig(self, label: str) -> int:
        """Given a figure label, return an integer corresponding to the figure number. If none is found, make a figure with that label and return the figure number

        This accounts for reuse of figures
        """
        if self.params.reuse_figures:
            # Try to find an existing plot for "Power". If none is available, make one
            fig_labels: List[str] = plt.get_figlabels()
            fig_number = 0
            try:
                fig_number = fig_labels.index(label)
            except ValueError:
                fig = plt.figure(label)
                fig_number: int = fig.number  # type: ignore
        else:
            fig = plt.figure()
            fig_number: int = fig.number  # type: ignore
        return fig_number


class PlotTotalEfficiencyCommand(Command):
    """Command to schedule plotting of total efficiency vs incident angle"""

    def __init__(self, receiver: PlotGenerator, efficiency_vs_incident_angles: np.ndarray, trial_label: str, title: str = None, error: np.ndarray = None, spr_angles: Dict[int, float] = None, woods: Dict[int, float] = None  # type: ignore
                 ):
        """Create command to plot total efficiency

        :param receiver: the object that will handle the logic associated with the command
        :param efficiency_vs_incident_angles: The data containing the thing to plot
        """
        self.receiver = receiver
        self.trial_label = trial_label
        self.title = title
        self.data = efficiency_vs_incident_angles
        self.error = error
        self.spr_angles = spr_angles
        self.woods = woods

    def execute(self):
        self.receiver.plot_total_efficiency(
            self.data, self.trial_label, title=self.title, error=self.error, spr_angles=self.spr_angles, woods=self.woods)


class ShowFigures(Command):
    """Command to show figures"""

    def __init__(self, receiver: PlotGenerator):
        self.receiver = receiver

    def execute(self):
        self.receiver.showfigures()


# class PlotEfficiencyCommand(Command):
#     """Command to schedule plotting of efficiency"""

#     def __init__(self, receiver: PlotGenerator, efficiency_vs_mirror_angles: Dict[float, np.ndarray], trial_label: str):
#         """Create a command to plot efficiency

#         :param receiver: the object that will handle the logic associated with the command
#         :param efficiency_vs_mirror_angles: The data containing the thing to plot
#         """
#         self.receiver = receiver
#         self.trial_label = trial_label
#         self.data = efficiency_vs_mirror_angles

#     def execute(self):
#         self.receiver.plot_efficiency(self.data, self.trial_label)


# class PlotPowerCommand(Command):
#     """Command to schedule plotting of power"""

#     def __init__(self, receiver: PlotGenerator, powers_vs_mirror_angles: Dict[float, np.ndarray], trial_label: str):
#         """Create a command to plot the powers

#         :param receiver: the object that will handle the logic associated with the command.
#         :param powers_vs_mirror_angles: The data containing the thing to plot
#         """
#         self.receiver = receiver
#         self.trial_label = trial_label
#         self.data = powers_vs_mirror_angles

#     def execute(self):
#         self.receiver.plot_powers(self.data, self.trial_label)
