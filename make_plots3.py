"""This is the old version of the plotting program prior to the separation of concerns."""
import pandas
import numpy as np
import matplotlib.pyplot as plt

class ComputeData:
    """A class to compute the data from each trial. Useful for fewer changes in code when changing experiment parameters."""
    def __init__(self, 
        full_data_set:np.array,
        incident_power_function,
        efficiency_function,
        power_a_column:int = 1, 
        power_b_column:int = 2, 
        grating_angle_column:int = 3, 
        mirror_angle_column:int = 4, 
        grating_angle_offset:int = 0):
        """Initializes the routine. The column parameters refer to the column positions in the numpy array to extract the corresponding values. Note that the efficiency function and the incident power function must have signatures of the form (power_1, power_2), where the powers are the measured powers and not transformed in some way. Mirror angle transformation accepts the object as input."""
        self.data = full_data_set
        self.efficiency = efficiency_function
        self.incident_power = incident_power_function
        self.power_a_column = power_a_column
        self.power_b_column = power_b_column
        self.grating_angle_column = grating_angle_column
        self.mirror_angle_column = mirror_angle_column
        self.grating_angle_offset = grating_angle_offset
    

    def compute_efficiency_vs_mirror_angle(self, 
        grating_angles_to_use:np.array, 
        remove_unphysical_points:bool=False, 
        background_threshold:float=0,
        custom_computer=0):
        """Computes the efficiency vs mirror angle for the given grating angles. The provided grating angles must be explicitly present in the data.
        
        If remove_unphysical_points is True, this removes the points that have efficiencies outside the domain [0, 1]. This defaults to False.
        If background_threshold is provided, efficiencies below this number are omitted.
        If custom_computer is provided, the method runs this function instead and returns the output. This function runs taking the same parameters as this method, and returns the same type."""
        if custom_computer:
            return custom_computer(self, grating_angles_to_use, remove_unphysical_points=remove_unphysical_points, background_threshold=background_threshold)
        
        result = dict() # append each grating angle to this dict

        for grating_angle in grating_angles_to_use:
            single_run = self.data[self.data[:, self.grating_angle_column] == grating_angle] #Get a given grating angle's data
            mirror_angles = single_run[:, self.mirror_angle_column]
            efficiency = self.efficiency(single_run[:, self.power_a_column], single_run[:, self.power_b_column])
            efficiency_vs_mirror_angle = np.column_stack((mirror_angles, efficiency)) # Combine data points to plot in 2D array, with mirror angle in first column and efficiency in the second
            

            if remove_unphysical_points:
                efficiency_vs_mirror_angle = efficiency_vs_mirror_angle[efficiency_vs_mirror_angle[:, 1] < 1] #Remove big outliers
                efficiency_vs_mirror_angle = efficiency_vs_mirror_angle[efficiency_vs_mirror_angle[:, 1] > 0] #Remove negative outliers
            if background_threshold:
                efficiency_vs_mirror_angle = efficiency_vs_mirror_angle[efficiency_vs_mirror_angle[:, 1] > background_threshold]
            
            result.update(
                {
                str(grating_angle-self.grating_angle_offset) : efficiency_vs_mirror_angle 
                }
            )
        
        return result
    

    def compute_efficiency_vs_grating_angle(self, 
        grating_angles_to_use:np.array,
        remove_unphysical_points:bool=False,
        background_threshold:float=0,
        custom_computer=0):
        """Computes the efficiency vs grating angle for the given grating angles. The provided grating angles must be explicitly present in the data.
        
        If remove_unphysical_points is True, this removes the points that have efficiencies outside the domain [0, 1]. This defaults to False.
        If background_threshold is provided, efficiencies below this number are omitted.
        If custom_computer is provided, the method runs this function instead and returns the output. This function runs taking the same parameters as this method, and returns the same type."""
        if custom_computer:
            return custom_computer(self, grating_angles_to_use, remove_unphysical_points=remove_unphysical_points, background_threshold=background_threshold)
        
        efficiency_vs_grating_angle = np.zeros((1, 2)) #Initialize empty array for loop; will remove this first value afterwards
        
        for grating_angle in grating_angles_to_use:
            single_run = self.data[self.data[:, self.grating_angle_column] == grating_angle] #Get a given grating angle's data
            efficiency = np.sum(
                self.efficiency(
                    single_run[:, self.power_a_column], 
                    single_run[:, self.power_b_column]
                )
            ) #Compute the summed efficiencies across entire run for that grating angle
            efficiency_vs_grating_angle = np.append(efficiency_vs_grating_angle, [[grating_angle-self.grating_angle_offset, efficiency]], axis=0) #Add the resulting data point to the array to matrix
        
        efficiency_vs_grating_angle = efficiency_vs_grating_angle[1:, :] #Remove the initialized value from the beginning

        if remove_unphysical_points:
            efficiency_vs_grating_angle = efficiency_vs_grating_angle[efficiency_vs_grating_angle[:, 1] < 1] #Remove big outliers
            efficiency_vs_grating_angle = efficiency_vs_grating_angle[efficiency_vs_grating_angle[:, 1] > 0] #Remove negative outliers
        if background_threshold:
            efficiency_vs_grating_angle = efficiency_vs_grating_angle[efficiency_vs_grating_angle[:, 1] > background_threshold]
        
        return efficiency_vs_grating_angle


    def compute_powers_vs_mirror_angle(self, 
        grating_angles_to_use:np.array,
        background_threshold:float=0,
        power_scale_factor:float=1,
        custom_computer=0):
        """Computes the powers vs mirror angle for the given grating angles. The provided grating angles must be explicitly present in the data.
        
        If background_threshold is provided, powers below this number (in units of power_scale_factor) are omitted.
        If power_scale_factor is provided, the power readings will all be scaled by this factor.
        If custom_computer is provided, the method runs this function instead and returns the output. This function runs taking the same parameters as this method, and returns the same type."""
        if custom_computer:
            return custom_computer(self, grating_angles_to_use, background_threshold=background_threshold, power_scale_factor=power_scale_factor)
        
        result = dict()
        for grating_angle in grating_angles_to_use:
            single_run = self.data[self.data[:, self.grating_angle_column] == grating_angle] #Get a given grating angle's data
            mirror_angles = single_run[:, self.mirror_angle_column]
            power_a = single_run[:, self.power_a_column]*power_scale_factor 
            power_b = single_run[:, self.power_b_column]*power_scale_factor 
            power_incident = self.incident_power(power_a, power_b)
        
            if background_threshold:
                background_threshold = background_threshold*power_scale_factor
                power_a = power_a[power_a > background_threshold]
                power_b = power_a[power_b > background_threshold]
                power_incident = power_incident[power_incident > background_threshold]
            
            powers_vs_mirror_angle = np.column_stack((mirror_angles, power_a, power_b, power_incident))

            result.update(
                {
                    str(grating_angle-self.grating_angle_offset) : powers_vs_mirror_angle
                }
            )
        
        return result

def plot_efficiency_vs_mirror_angle(data, figure_number:int, **kwargs):
    """Plots efficiency vs. mirror angle.
    
    Valid kwargs:
    point_shape: pyplot data point shape."""
    point_shape = kwargs.pop("point_shape", None)
    plt.figure(figure_number) #Tells the plotter to do operations on the given figure, referenced via the figure number
    for grating_angle, data in data.items():
        plt.scatter(data[:, 0], data[:, 1], s=8.0, label=grating_angle, marker=(point_shape if point_shape is not None else ".")) # Plot efficiency vs mirror angle and label the series as "angle" where angle is the numerical angle (adjusted to normal incidence)
    plt.legend(loc="upper left")
    plt.legend(loc="best")
#    plt.title("log of Efficiency vs. Mirror angle, with efficiency < 0.01 removed")
    plt.title("log of Efficiency vs. Mirror angle")
    # plt.margins(y=10.0)
    plt.grid(which="both", axis="both")
    plt.yscale("log")
    plt.xlabel('mirror angle ($^\circ$)')
    plt.ylabel('$log_{10}$(efficiency)')

def plot_efficiency_vs_grating_angle(data:np.array, label:str, figure_number:int):
    """Plots efficiency vs grating angle for the provided data. Requires the figure number to plot on, and the label to place on the series."""
    plt.figure(figure_number)
    plt.scatter(data[:, 0], data[:, 1], s=10.0, label=label) #plot data
    plt.title("Efficiency vs. grating angle")
    # plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
    plt.xlabel('grating angle ($^\circ$)')
    plt.ylabel('efficiency')
    plt.grid(which="both", axis="both")
    plt.legend()

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

def plot_powers_vs_mirror_angle(data:dict, figure_number:int):
    plt.figure(figure_number)
    for grating_angle, powers_vs_mirror_angle in data.items():
        plt.scatter(powers_vs_mirror_angle[:, 0], powers_vs_mirror_angle[:, 1], s=5.0, label=f"A at {grating_angle}")
        plt.scatter(powers_vs_mirror_angle[:, 0], powers_vs_mirror_angle[:, 2], s=5.0, label=f"B at {grating_angle}", marker="v")
        plt.scatter(powers_vs_mirror_angle[:, 0], powers_vs_mirror_angle[:, 3], s=5.0, label=f"Incident at {grating_angle}", marker="x")
    # plt.legend(loc="best")
    plt.legend(bbox_to_anchor=(1.10, 1), loc='upper right', borderaxespad=0)
    plt.ticklabel_format(axis="y") #, style="sci", scilimits=(0,0)
    plt.grid(which="both", axis='both')
    plt.xlabel('mirror angle ($^\circ$)')
    plt.yscale("log")
    plt.ylabel('$log_{10}$(power) ($\mu$W)')
    plt.title(f"Grating angles: {', '.join([k for k in data.keys()])}")
    plt.suptitle("Powers vs. mirror angle")
    return


if __name__ == "__main__":

    """Here I define the custom computers that would override each method"""
    def efficiency_vs_mirror_angle_override(
        data_computer:ComputeData, 
        grating_angles:np.array,
        remove_unphysical_points:bool=False,
        background_threshold:float=0):
        """Computes the efficiency vs mirror angle for the given grating angles. The provided grating angles must be explicitly present in the data.
        
        If remove_unphysical_points is True, this removes the points that have efficiencies outside the domain [0, 1]. This defaults to False.
        If background_threshold is provided, efficiencies below this number are omitted"""
        result = dict() # append each grating angle to this dict
        
        for grating_angle in grating_angles:
            single_run = data_computer.data[data_computer.data[:, data_computer.grating_angle_column] == grating_angle] #Get a given grating angle's data
            # mirror_angles = np.fmod(single_run[:, 5], 360) + 90 - grating_angle #get mirror angles as expected
            mirror_angles = single_run[:, data_computer.mirror_angle_column]
            """Here is where the override function differs from the default method. I use a fixed value for sensor A, since we occasionally have weird values for A"""
            efficiency = data_computer.efficiency(1.222300*10**-5, single_run[:, data_computer.power_b_column]) #Here I put some random "good" value for the power A, since Power A's electronics are a little funny
            efficiency_vs_mirror_angle = np.column_stack((mirror_angles, efficiency)) # Combine data points to plot in 2D array, with mirror angle in first column and efficiency in the second
            

            if remove_unphysical_points:
                efficiency_vs_mirror_angle = efficiency_vs_mirror_angle[efficiency_vs_mirror_angle[:, 1] < 1] #Remove big outliers
                efficiency_vs_mirror_angle = efficiency_vs_mirror_angle[efficiency_vs_mirror_angle[:, 1] > 0] #Remove negative outliers
            if background_threshold:
                efficiency_vs_mirror_angle = efficiency_vs_mirror_angle[efficiency_vs_mirror_angle[:, 1] > background_threshold]
            
            result.update(
                {
                str(grating_angle-data_computer.grating_angle_offset) : efficiency_vs_mirror_angle 
                }
            )
        
        return result

    def efficiency_vs_grating_angle_override(
        data_computer:ComputeData, 
        grating_angles_to_use:np.array,
        remove_unphysical_points:bool=False,
        background_threshold:float=0):
        """Computes the efficiency vs grating angle for the given grating angles. The provided grating angles must be explicitly present in the data.
        
        If remove_unphysical_points is True, this removes the points that have efficiencies outside the domain [0, 1]. This defaults to False.
        If background_threshold is provided, efficiencies below this number are omitted."""
        
        efficiency_vs_grating_angle = np.zeros((1, 2)) #Initialize empty array for loop; will remove this first value afterwards
        
        for grating_angle in grating_angles_to_use:
            single_run = data_computer.data[data_computer.data[:, data_computer.grating_angle_column] == grating_angle] #Get a given grating angle's data
            """Here is where the override function differs from the default method. I use a fixed value for sensor A, since we occasionally have weird values for A"""
            efficiency = np.sum(
                data_computer.efficiency(
                    1.222300*10**-5, 
                    single_run[:, data_computer.power_b_column]
                )
            ) 
            efficiency_vs_grating_angle = np.append(efficiency_vs_grating_angle, [[grating_angle-data_computer.grating_angle_offset, efficiency]], axis=0) #Add the resulting data point to the array to matrix
        
        efficiency_vs_grating_angle = efficiency_vs_grating_angle[1:, :] #Remove the initialized value from the beginning

        if remove_unphysical_points:
            efficiency_vs_grating_angle = efficiency_vs_grating_angle[efficiency_vs_grating_angle[:, 1] < 1] #Remove big outliers
            efficiency_vs_grating_angle = efficiency_vs_grating_angle[efficiency_vs_grating_angle[:, 1] > 0] #Remove negative outliers
        if background_threshold:
            efficiency_vs_grating_angle = efficiency_vs_grating_angle[efficiency_vs_grating_angle[:, 1] > background_threshold]
        
        return efficiency_vs_grating_angle

    def powers_vs_mirror_angle_override(
        data_computer:ComputeData, 
        grating_angles_to_use:np.array,
        background_threshold:float=0,
        power_scale_factor:float=1):
        """Computes the powers vs mirror angle for the given grating angles. The provided grating angles must be explicitly present in the data.
        
        If background_threshold is provided, powers below this number (in units of power_scale_factor) are omitted.
        If power_scale_factor is provided, the power readings will all be scaled by this factor."""
        
        result = dict()
        for grating_angle in grating_angles_to_use:
            single_run = data_computer.data[data_computer.data[:, data_computer.grating_angle_column] == grating_angle] #Get a given grating angle's data
            mirror_angles = np.fmod(single_run[:, 5], 360) + 90 - grating_angle #get mirror angles as expected
            power_a = single_run[:, data_computer.power_a_column]*power_scale_factor 
            power_b = single_run[:, data_computer.power_b_column]*power_scale_factor 
            power_incident = data_computer.incident_power(power_a, power_b)
        
            if background_threshold:
                background_threshold = background_threshold*power_scale_factor
                power_a = power_a[power_a > background_threshold]
                power_b = power_a[power_b > background_threshold]
                power_incident = power_incident[power_incident > background_threshold]
            
            powers_vs_mirror_angle = np.column_stack((mirror_angles, power_a, power_b, power_incident))

            result.update(
                {
                    str(grating_angle-data_computer.grating_angle_offset) : powers_vs_mirror_angle
                }
            )
        
        return result

    """Here I import requisite libraries, bind files, etc."""
    from pathlib import Path
    trial_folder1= Path("Trials/GH13-12V (B to the right) (2)") #The parent folder containing the parameter csv and the data csv
    data_csv1 = trial_folder1 / "data.csv" #The raw data
    computation_parameters_csv1 = trial_folder1 / "computation_parameters.csv" #The parameters
    computation_parameters1 = pandas.read_csv(computation_parameters_csv1) #Read it into panda dataframe

    trial_folder2= Path("Trials/GH13-12V (B to the right) (1)/") #The parent folder containing the parameter csv and the data csv
    data_csv2 = trial_folder2 / "data.csv" #The raw data
    computation_parameters_csv2 = trial_folder2 / "computation_parameters.csv" #The parameters
    computation_parameters2 = pandas.read_csv(computation_parameters_csv2) #Read it into panda dataframe

    """I am only selecting the data that will be used in computation for this trial"""
    reflectivity_coefficient = computation_parameters1['R'][0] #For sensor A
    grating_angle_offset = computation_parameters1["Grating Angle Offset"][0] #For shifting the grating motor angle's origin to set incidence angle to zero rather than something else
    sensor_a_background = computation_parameters1["Background Power (W)"][0]
    sensor_b_background = computation_parameters1["Background Power (W)"][1]
    full_set1 = pandas.read_csv(data_csv1, header=None).iloc[:].to_numpy(dtype=np.double) #Read in the raw data as a numpy matrix
    full_set2 = pandas.read_csv(data_csv2, header=None).iloc[:].to_numpy(dtype=np.double) #Read in the raw data as a numpy matrix
    
    """Setting the column numbers that correspond to each measurement. Example: the 2nd column contains the powers from power sensor A"""
    power_a_column = 1
    power_b_column = 2
    grating_angle_column = 3
    mirror_angle_column = 4
    """Instantiating figures for simultaneous plotting"""
    plt.figure(1) #efficiency_vs_mirror_angle figure initialization
    plt.figure(2) #efficiency_vs_grating_angle figure initialization
    plt.figure(3) #powers_vs_mirror_angle figure initialization

    """Here I define a lambda function to compute the indicent power for this trial. In this case, that is simply the reflected power (power sensor A) divided by the reflectivity coefficient"""
    incident_power = lambda power_a, power_b: (power_a - sensor_a_background)/reflectivity_coefficient
    """Here I define a lambda function to compute the efficiency, where sensor B is measuring transmitted power and sensor A is used to compute incident power"""
    eff_2 = lambda power_a, power_b: (power_b-sensor_b_background)/(((power_a - sensor_a_background)/reflectivity_coefficient) - (power_a - sensor_a_background))
    """Here I make the object from the class, passing in the previous functions to compute the incident power and efficiency, as well as which columns in the data correspond to which values."""
    comp1 = ComputeData(full_set1,
        incident_power_function=incident_power,
        efficiency_function=eff_2,
        power_a_column=power_a_column, 
        power_b_column=power_b_column, 
        grating_angle_column=grating_angle_column, 
        mirror_angle_column=mirror_angle_column,
        grating_angle_offset=grating_angle_offset
        )
    
    comp2 = ComputeData(full_set2,
        incident_power_function=incident_power,
        efficiency_function=eff_2,
        power_a_column=power_a_column, 
        power_b_column=power_b_column, 
        grating_angle_column=grating_angle_column, 
        mirror_angle_column=mirror_angle_column,
        grating_angle_offset=grating_angle_offset
        )

    """Now we do actual computation here!"""
    grating_angles_to_use = np.array(np.array([-50, 0, 50])) #Change these to whatever incident angles you want!
    """Efficiency vs grating angle, computed using the override function. The specific thing I override in that function is how the efficiency is computed, since we have some problems with sensor A at certain values."""
    efficiency_vs_grating_angle1 = comp1.compute_efficiency_vs_grating_angle(grating_angles_to_use, remove_unphysical_points=False, custom_computer=efficiency_vs_grating_angle_override)
    """Same as above, but for mirror angles."""
    efficiency_vs_mirror_angle1 = comp1.compute_efficiency_vs_mirror_angle(grating_angles_to_use, remove_unphysical_points=False, background_threshold=0, custom_computer=efficiency_vs_mirror_angle_override)
    """Here I use the default method to produce the powers vs. mirror angles data."""
    powers_vs_mirror_angle1 = comp1.compute_powers_vs_mirror_angle(grating_angles_to_use, power_scale_factor=1e6)
    """Here I plot."""
    plot_efficiency_vs_grating_angle(efficiency_vs_grating_angle1, "Down orientation", 1)
    plot_efficiency_vs_mirror_angle(efficiency_vs_mirror_angle1, 2, point_shape="v")
    plot_powers_vs_mirror_angle(powers_vs_mirror_angle1, 3)

    """Efficiency vs grating angle, computed using the override function. The specific thing I override in that function is how the efficiency is computed, since we have some problems with sensor A at certain values."""
    efficiency_vs_grating_angle2 = comp2.compute_efficiency_vs_grating_angle(grating_angles_to_use, remove_unphysical_points=False, custom_computer=efficiency_vs_grating_angle_override)
    """Same as above, but for mirror angles."""
    efficiency_vs_mirror_angle2 = comp2.compute_efficiency_vs_mirror_angle(grating_angles_to_use, remove_unphysical_points=False, background_threshold=0, custom_computer=efficiency_vs_mirror_angle_override)
    """Here I use the default method to produce the powers vs. mirror angles data."""
    powers_vs_mirror_angle2 = comp2.compute_powers_vs_mirror_angle(grating_angles_to_use, power_scale_factor=1e6)
    """Here I plot."""
    plot_efficiency_vs_grating_angle(efficiency_vs_grating_angle2, "Up orientation", 1)
    plot_efficiency_vs_mirror_angle(efficiency_vs_mirror_angle2, 2, point_shape="^")
    plot_powers_vs_mirror_angle(powers_vs_mirror_angle2, 3)
    plt.show()