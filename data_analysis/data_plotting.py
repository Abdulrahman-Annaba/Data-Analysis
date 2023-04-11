"""Module focused on plotting the data."""

# Import pyplot and numpy
import matplotlib.pyplot as plt
import numpy as np


def plot_efficiency_vs_mirror_angle(data, figure_number:int, **kwargs):
    """Plots efficiency vs. mirror angle.
    
    Valid kwargs:
    point_shape: pyplot data point shape.
    label_prefix: what to prefix grating angles for this set of data"""
    # Get valid kwargs
    label_prefix = kwargs.pop("label_prefix", None)
    point_shape = kwargs.pop("point_shape", None)
    # Move plotter to the provided figure number
    plt.figure(figure_number)
    # Loop over grating angles and their respective data
    for grating_angle, efficiencies_vs_mirror_angle in data.items():
        # Set label_prefix if provided, otherwise make it an empty string
        label_prefix = label_prefix if label_prefix is not None else ""
        plt.scatter(
            efficiencies_vs_mirror_angle[:, 0],
            efficiencies_vs_mirror_angle[:, 1],
            label=f"{label_prefix}{grating_angle}", 
            marker=(point_shape if point_shape is not None else "."),
            s=50
            )
    # Set cosmetic figure things to make it human readable, or whatever. Most importantly, put the legend away from the plotted region.
    plt.legend(bbox_to_anchor=(1.10, 1), loc='upper right', borderaxespad=0)
    plt.ticklabel_format(axis="y") #, style="sci", scilimits=(0,0)
    plt.grid(which="both", axis='both')
    plt.xlabel('mirror angle ($^\circ$)')
    plt.yscale("log")
    plt.ylabel('$log_{10}$(efficiency)')
    plt.suptitle("Efficiency vs. mirror angle")
    return

def plot_efficiency_vs_incident_angle(data:np.array, figure_number:int, **kwargs):
    """Plots efficiency vs incident angle for the provided data. Requires the figure number to plot on.
    
    kwargs:
    label: label to add to figure
    spr_angles: a dictionary of diffraction orders and incident angles at which SPR can occur. When provided, adds vertical lines at these incident angles demonstrating locations of theoretical predictions for SPR"""
    label = kwargs.pop("label", None)
    spr_angles = kwargs.pop("spr_angles", None)
    plt.figure(figure_number)
    if label is not None:
        plt.plot(data[:, 0], data[:, 1], label=label) #plot data
    else:
        plt.plot(data[:, 0], data[:, 1]) #plot data
    if spr_angles is not None:
        for order, spr_angle in spr_angles.items():
            plt.axvline(x=spr_angle, color='b', label=f"{label}: SPR order {order}")
    plt.title("Efficiency vs. incident angle")
    # plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
    plt.xlabel('incident angle ($^\circ$)')
    plt.ylabel('efficiency')
    plt.grid(which="both", axis="both")
    plt.legend()

def plot_powers_vs_mirror_angle(data:dict, figure_number:int, **kwargs):
    """Plots power vs mirror angle.
    
    Optional arguments:
    label_prefix: A string to prefix prior to the series in the legend."""
    # Get valid kwargs
    label_prefix = kwargs.pop("label_prefix", None)
    # Move plotter to the provided figure number
    plt.figure(figure_number)
    # Loop over grating angles and their respective data
    for grating_angle, powers_vs_mirror_angle in data.items():
        # Set label_prefix if provided, otherwise make it an empty string
        label_prefix = label_prefix if label_prefix is not None else ""
        # Plot the power data (Power A, power B, and Incident Power vs. mirror angle)
        # My crappy reasons for why I chose the markers I chose:
        # Chose . for power A's marker just because it's the first.
        # Chose v for power B's marker just because it's lower in the experiment.
        # Chose x for incident power because it's like a vector going into the experiment.
        # I know. Crappy, right?
        plt.scatter(powers_vs_mirror_angle[:, 0], powers_vs_mirror_angle[:, 1], s=5.0, label=f"{label_prefix}A at {grating_angle}", marker="v")
        plt.scatter(powers_vs_mirror_angle[:, 0], powers_vs_mirror_angle[:, 2], s=5.0, label=f"{label_prefix}B at {grating_angle}", marker="v")
        plt.scatter(powers_vs_mirror_angle[:, 0], powers_vs_mirror_angle[:, 3], s=5.0, label=f"{label_prefix}Incident at {grating_angle}", marker="x")
    # Set cosmetic figure things to make it human readable, or whatever. Most importantly, put the legend away from the plotted region.
    plt.legend(bbox_to_anchor=(1.10, 1), loc='upper right', borderaxespad=0)
    plt.ticklabel_format(axis="y") #, style="sci", scilimits=(0,0)
    plt.grid(which="both", axis='both')
    plt.xlabel('mirror angle ($^\circ$)')
    plt.yscale("log")
    plt.ylabel('$log_{10}$(power) ($\mu$W)')
    plt.suptitle("Powers vs. mirror angle")
    return