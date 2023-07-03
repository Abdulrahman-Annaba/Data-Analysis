"""Module focused on plotting the data."""

# Import pyplot and numpy
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
from typing import Dict

# TODO: finish these other commented functions

# def plot_efficiency_vs_mirror_angle(data, figure_number: int, **kwargs):
#     """Plots efficiency vs. mirror angle.

#     Valid kwargs:
#     point_shape: pyplot data point shape.
#     label_prefix: what to prefix grating angles for this set of data"""
#     # Get valid kwargs
#     label_prefix = kwargs.pop("label_prefix", None)
#     point_shape = kwargs.pop("point_shape", None)
#     # Move plotter to the provided figure number
#     plt.figure(figure_number)
#     # Loop over grating angles and their respective data
#     for grating_angle, efficiencies_vs_mirror_angle in data.items():
#         # Set label_prefix if provided, otherwise make it an empty string
#         label_prefix = label_prefix if label_prefix is not None else ""
#         plt.scatter(
#             efficiencies_vs_mirror_angle[:, 0],
#             efficiencies_vs_mirror_angle[:, 1],
#             label=f"{label_prefix}{grating_angle}",
#             marker=(point_shape if point_shape is not None else "."),
#             s=50
#         )
#     # Set cosmetic figure things to make it human readable, or whatever. Most importantly, put the legend away from the plotted region.
#     plt.legend(bbox_to_anchor=(1.10, 1), loc='upper right', borderaxespad=0)
#     plt.ticklabel_format(axis="y")  # , style="sci", scilimits=(0,0)
#     plt.grid(which="both", axis='both')
#     plt.xlabel('mirror angle ($^\circ$)')
#     plt.yscale("log")
#     plt.ylabel('$log_{10}$(efficiency)')
#     plt.suptitle("Efficiency vs. mirror angle")
#     return


def plot_efficiency_vs_incident_angle(data: np.ndarray, figure_number: int, series_label: str = None, title: str = None, error: np.ndarray = None, spr_angles: Dict[int, float] = None, woods: Dict[int, float] = None  # type: ignore
                                      ):
    """Plots efficiency vs incident angle for the provided data. Requires the figure number to plot on.

    kwargs:
    label: label to add to series
    spr_angles: a dictionary of diffraction orders and incident angles at which SPR can occur. When provided, adds vertical lines at these incident angles demonstrating locations of theoretical predictions for SPR
    woods: a dictionary of diffraction orders and incident angles at which woods anomalies can occur. When provided, adds vertical lines at these incident angles demonstrating locations of theoretical predictions for woods anomalies
    title: Optional string to use as the title of the plot. Default to None."""
    figure = plt.figure(figure_number)
    # Hard code size to be 21 inches by 12 inches
    # TODO: Make this better
    figure.set_size_inches(21, 12)
    plt.scatter(data[:, 0], data[:, 1])  # plot data
    if series_label is not None:
        if error is not None:
            plt.errorbar(data[:, 0], data[:, 1],
                         yerr=error[:, 1], label=series_label, ecolor='red', barsabove=True)
        else:
            plt.plot(data[:, 0], data[:, 1], label=series_label)
    else:
        if error is not None:
            plt.errorbar(data[:, 0], data[:, 1],
                         yerr=error[:, 1], ecolor='red', barsabove=True)
        else:
            plt.plot(data[:, 0], data[:, 1])
    if spr_angles is not None:
        # Set state variable to prevent multiple relabelings from appearing in legend
        labeled_spr = False
        for order, spr_angle in spr_angles.items():
            if not labeled_spr:
                plt.axvline(x=spr_angle, color='b', label="SPR")
                labeled_spr = True
            else:
                plt.axvline(x=spr_angle, color='b')
    if woods is not None:
        labeled_woods = False
        for order, wood_angle in woods.items():
            if not labeled_woods:
                plt.axvline(x=wood_angle, color='r', label="Wood's anomalies")
                labeled_woods = True
            else:
                plt.axvline(x=wood_angle, color='r')
    plt.title("Efficiency vs. incident angle" if title is None else title)
    # plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
    plt.xlabel('incident angle ($^\circ$)')
    figure.axes[0].xaxis.set_major_locator(ticker.MultipleLocator(5))
    figure.axes[0].xaxis.set_minor_locator(ticker.MultipleLocator(1))
    figure.axes[0].yaxis.set_major_locator(ticker.MultipleLocator(0.1))
    figure.axes[0].yaxis.set_minor_locator(ticker.MultipleLocator(0.01))
    figure.axes[0].grid(b=True, which='major', axis='both')
    # Hard code vertical bounds to be from 0 to 1 (as expected for efficiency)
    figure.axes[0].set_ylim(bottom=0, top=1)
    plt.ylabel('efficiency')
    plt.legend()
    plt.tight_layout()


# def plot_powers_vs_mirror_angle(data: dict, figure_number: int, **kwargs):
#     """Plots power vs mirror angle.

#     Optional arguments:
#     label_prefix: A string to prefix prior to the series in the legend."""
#     # Get valid kwargs
#     label_prefix = kwargs.pop("label_prefix", None)
#     # Move plotter to the provided figure number
#     plt.figure(figure_number)
#     # Loop over grating angles and their respective data
#     for grating_angle, powers_vs_mirror_angle in data.items():
#         # Set label_prefix if provided, otherwise make it an empty string
#         label_prefix = label_prefix if label_prefix is not None else ""
#         # Plot the power data (Power A, power B, and Incident Power vs. mirror angle)
#         # My crappy reasons for why I chose the markers I chose:
#         # Chose . for power A's marker just because it's the first.
#         # Chose v for power B's marker just because it's lower in the experiment.
#         # Chose x for incident power because it's like a vector going into the experiment.
#         # I know. Crappy, right?
#         plt.scatter(powers_vs_mirror_angle[:, 0], powers_vs_mirror_angle[:, 1],
#                     s=5.0, label=f"{label_prefix}A at {grating_angle}", marker="v")
#         plt.scatter(powers_vs_mirror_angle[:, 0], powers_vs_mirror_angle[:, 2],
#                     s=5.0, label=f"{label_prefix}B at {grating_angle}", marker="v")
#         plt.scatter(powers_vs_mirror_angle[:, 0], powers_vs_mirror_angle[:, 3],
#                     s=5.0, label=f"{label_prefix}Incident at {grating_angle}", marker="x")
#     # Set cosmetic figure things to make it human readable, or whatever. Most importantly, put the legend away from the plotted region.
#     plt.legend(bbox_to_anchor=(1.10, 1), loc='upper right', borderaxespad=0)
#     plt.ticklabel_format(axis="y")  # , style="sci", scilimits=(0,0)
#     plt.grid(which="both", axis='both')
#     plt.xlabel('mirror angle ($^\circ$)')
#     plt.yscale("log")
#     plt.ylabel('$log_{10}$(power) ($\mu$W)')
#     plt.suptitle("Powers vs. mirror angle")
#     return
