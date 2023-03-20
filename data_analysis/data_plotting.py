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
        # Plot the unmasked data first
        plt.scatter(
            efficiencies_vs_mirror_angle[:, 0],
            efficiencies_vs_mirror_angle[:, 1],
            label=f"{label_prefix}{grating_angle}", 
            marker=(point_shape if point_shape is not None else "."),
            s=50
            )
        # Now plot the masked data as a separate series
        plt.scatter(
            np.asarray(efficiencies_vs_mirror_angle[:, 0][efficiencies_vs_mirror_angle[:, 1].mask]),
            np.asarray(efficiencies_vs_mirror_angle[:, 1][efficiencies_vs_mirror_angle[:, 1].mask]),
            label=f"{label_prefix}Approximated A at {grating_angle}",
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

def plot_efficiency_vs_grating_angle(data:np.array, figure_number:int, **kwargs):
    """Plots efficiency vs grating angle for the provided data. Requires the figure number to plot on.
    
    kwargs:
    label: label to add to figure"""
    label = kwargs.pop("label", None)
    plt.figure(figure_number)
    if label is not None:
        plt.plot(data[:, 0], data[:, 1], label=label) #plot data
    else:
        plt.plot(data[:, 0], data[:, 1]) #plot data
    plt.title("Efficiency vs. grating angle")
    # plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
    plt.xlabel('grating angle ($^\circ$)')
    plt.ylabel('efficiency')
    plt.grid(which="both", axis="both")
    plt.legend()

"""Old code here. Keeping this commented in case we need some parts of it in the future."""

# def compute_efficiency_vs_grating_angle2(grating_angles_to_use:np.array) -> tuple[np.array]:
#     grating_angles = grating_angles_to_use #Get the grating angles vector
#     #Now separate the data set into single runs
#     efficiency_vs_grating_angle = np.zeros((1,2)) #Initialize empty array for loop; will remove this first value afterwards
#     efficiency_to_use = np.zeros((1, 1)) #Initialize empty array for loop; will remove this first value afterwards
#     for grating_angle in grating_angles:
#         single_run = full_set[full_set[:, 3] == grating_angle] #Get a given grating angle's data
#         efficiency = np.sum((single_run[:, 1] - sensor_a_background)/((single_run[:, 2] - sensor_b_background)/reflectivity_coefficient-(single_run[:, 2] - sensor_b_background))) #Compute the summed efficiencies across entire run for that grating angle
#         efficiency_vs_grating_angle = np.append(efficiency_vs_grating_angle, [[grating_angle-grating_angle_offset, efficiency]], axis=0) #Add the resulting data point to the array to plot
#         if grating_angle in grating_angles_to_use:
#             efficiency_to_use = np.append(efficiency_to_use, efficiency)
#     efficiency_vs_grating_angle = efficiency_vs_grating_angle[1:, :] #Remove the initialized value from the beginning
#     efficiency_to_use = efficiency_to_use[1:] #Remove the initialized value from the beginning
#     efficiency_vs_grating_angle = efficiency_vs_grating_angle[efficiency_vs_grating_angle[:, 1] < 3] #Remove big outliers
#     efficiency_vs_grating_angle = efficiency_vs_grating_angle[efficiency_vs_grating_angle[:, 1] > 0] #Remove negative outliers
#     return (efficiency_vs_grating_angle, efficiency_to_use)

# def plot_efficiency_vs_grating_angle2(efficiency_vs_grating_angle:np.array, efficiency_to_use:np.array, figure_number:int):
#     plt.figure(figure_number)
#     plt.scatter(efficiency_vs_grating_angle[:, 0], efficiency_vs_grating_angle[:, 1], s=10.0) #plot data
#     plt.scatter([grating_angles_to_use-grating_angle_offset], efficiency_to_use, s=10.0, c="red") #plot single angle data
#     plt.title("Efficiency vs. grating angle")
#     plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
#     plt.xlabel('grating angle ($^\circ$)')
#     plt.ylabel('efficiency')    
#     plt.grid(which="both", axis="both")

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
        plt.scatter(np.asarray(powers_vs_mirror_angle[:, 0][powers_vs_mirror_angle[:, 1].mask]), np.asarray(powers_vs_mirror_angle[:, 1][powers_vs_mirror_angle[:, 1].mask]), s=5.0, label=f"{label_prefix}Approximated A at {grating_angle}")
        plt.scatter(powers_vs_mirror_angle[:, 0], powers_vs_mirror_angle[:, 2], s=5.0, label=f"{label_prefix}B at {grating_angle}", marker="v")
        plt.scatter(np.asarray(powers_vs_mirror_angle[:, 0][powers_vs_mirror_angle[:, 2].mask]), np.asarray(powers_vs_mirror_angle[:, 2][powers_vs_mirror_angle[:, 2].mask]), s=5.0, label=f"{label_prefix}Approximated B at {grating_angle}")
        plt.scatter(powers_vs_mirror_angle[:, 0], powers_vs_mirror_angle[:, 3], s=5.0, label=f"{label_prefix}Incident at {grating_angle}", marker="x")
        plt.scatter(np.asarray(powers_vs_mirror_angle[:, 0][powers_vs_mirror_angle[:, 3].mask]), np.asarray(powers_vs_mirror_angle[:, 3][powers_vs_mirror_angle[:, 3].mask]), s=5.0, label=f"{label_prefix}Approximated Incident at {grating_angle}")
    # Set cosmetic figure things to make it human readable, or whatever. Most importantly, put the legend away from the plotted region.
    plt.legend(bbox_to_anchor=(1.10, 1), loc='upper right', borderaxespad=0)
    plt.ticklabel_format(axis="y") #, style="sci", scilimits=(0,0)
    plt.grid(which="both", axis='both')
    plt.xlabel('mirror angle ($^\circ$)')
    plt.yscale("log")
    plt.ylabel('$log_{10}$(power) ($\mu$W)')
    plt.suptitle("Powers vs. mirror angle")
    return