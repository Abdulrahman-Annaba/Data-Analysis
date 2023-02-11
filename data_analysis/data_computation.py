"""Module focused on computing the provided data and providing the arrays (to be plotted)"""

import numpy as np
import pandas as pd

class Trial:

    """A class to compute the data from each trial. Useful for fewer changes in code when changing experiment parameters."""
    def __init__(self, 
        trial_label: str,
        full_data_set:np.array,
        incident_power_function,
        efficiency_function,
        slide_coefficients: pd.DataFrame,
        sensor_a_background: float,
        sensor_b_background: float,
        power_a_column:int = 1, 
        power_b_column:int = 2, 
        grating_angle_column:int = 3, 
        mirror_angle_column:int = 4, 
        grating_angle_offset:int = 0
        ):
        """Initializes the routine. The column parameters refer to the column positions in the numpy array to extract the corresponding values. Note that the efficiency function and the incident power function accept three arguments, the trial object itself, power_a, and power_b."""
        self.data = full_data_set
        self.trial_label = trial_label
        self.efficiency = efficiency_function
        self.incident_power = incident_power_function
        self.power_a_column = power_a_column
        self.power_b_column = power_b_column
        self.grating_angle_column = grating_angle_column
        self.mirror_angle_column = mirror_angle_column
        self.grating_angle_offset = grating_angle_offset
        self.slide_coefficients = slide_coefficients
        self.sensor_a_background = sensor_a_background
        self.sensor_b_background = sensor_b_background

    def compute_efficiency_vs_mirror_angle(self, 
        grating_angles_to_use:np.array, 
        remove_unphysical_points:bool=False, 
        background_threshold:float=0,
        custom_computer=0):
        """Computes the efficiency vs mirror angle for the given grating angles. The provided grating angles must be explicitly present in the data.
        
        If remove_unphysical_points is True, this removes the points that have efficiencies outside the domain [0, 1]. This defaults to False.
        If background_threshold is provided, efficiencies below this number are omitted.
        If custom_computer is provided, the method runs this function instead and returns the output. This function must run taking the same parameters as this method, and must return the same type."""
        
        # If doing a custom computation, call the provided function via the following signature. Will error if not correct.
        if custom_computer:
            return custom_computer(self, grating_angles_to_use, remove_unphysical_points=remove_unphysical_points, background_threshold=background_threshold)
        
        # Initialize a dictionary to append each grating angle and its associated data
        result = dict()

        # Loop over grating angles provided
        for grating_angle in grating_angles_to_use:
            # Get all the data points corresponding to a single grating angle
            single_run = self.data[self.data[:, self.grating_angle_column] == grating_angle] #Get a given grating angle's data
            # Get the numpy array of mirror anglese
            mirror_angles = single_run[:, self.mirror_angle_column]
            # Compute the efficiency, using the standard signature of (Trial, power_a, power_b)
            efficiency = self.efficiency(self, single_run[:, self.power_a_column], single_run[:, self.power_b_column])
            # combine the two columns together
            efficiency_vs_mirror_angle = np.column_stack((mirror_angles, efficiency)) # Combine data points to plot in 2D array, with mirror angle in first column and efficiency in the second
            
            # If enabled, remove the data points less than zero or greater than 1 (for bad data)
            if remove_unphysical_points:
                efficiency_vs_mirror_angle = efficiency_vs_mirror_angle[efficiency_vs_mirror_angle[:, 1] < 1] #Remove big outliers
                efficiency_vs_mirror_angle = efficiency_vs_mirror_angle[efficiency_vs_mirror_angle[:, 1] > 0] #Remove negative outliers
            # Omit data points below a certain threshold. Useful for focusing on large spikes in efficiency.
            if background_threshold:
                efficiency_vs_mirror_angle = efficiency_vs_mirror_angle[efficiency_vs_mirror_angle[:, 1] > background_threshold]
            
            # Label each series as grating angle, no trial label
            result.update(
                {
                f"{str(grating_angle-self.grating_angle_offset)}" : efficiency_vs_mirror_angle 
                }
            )
        
        # Return results
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
                    self,
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
            power_incident = self.incident_power(self, single_run[:, self.power_a_column], single_run[:, self.power_b_column])*power_scale_factor
        
            if background_threshold:
                background_threshold = background_threshold*power_scale_factor
                power_a = power_a[power_a > background_threshold]
                power_b = power_a[power_b > background_threshold]
                power_incident = power_incident[power_incident > background_threshold]
            
            powers_vs_mirror_angle = np.column_stack((mirror_angles, power_a, power_b, power_incident))

            result.update(
                {
                    f"{str(grating_angle-self.grating_angle_offset)}" : powers_vs_mirror_angle
                }
            )
        
        return result

def default_incident_power(trial: Trial, power_a, power_b):
    """Default incident power function. Assumes power sensor A is measuring the reflected power off the slide. This uses the first value for power sensor A in the entire trial, since power sensor A is faulty"""
    reflectivity = trial.slide_coefficients.loc["A"]["R"] # Get the reflection coefficient for sensor A
    power_a = np.broadcast_to(np.array([trial.data[0, trial.power_a_column]]), power_b.shape)
    return (power_a - trial.sensor_a_background)/reflectivity

def default_efficiency(trial: Trial, power_a, power_b):
    """Default efficiency function. This uses the first value for power sensor A in the entire trial, since power sensor A is faulty"""
    reflectivity = trial.slide_coefficients.loc["A"]["R"]
    power_a = np.broadcast_to(np.array([trial.data[0, trial.power_a_column]]), power_b.shape)
    return (power_b-trial.sensor_b_background)/(((power_a - trial.sensor_a_background)/reflectivity) - (power_a - trial.sensor_a_background))
