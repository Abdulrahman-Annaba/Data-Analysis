"""Module focused on computing the provided data and providing the arrays (to be plotted)"""

import numpy as np
import numpy.ma as ma
import pandas as pd
import scipy.stats._binned_statistic as binstat

BIN_AVERAGE_BINS = np.array([10**i for i in range(-10, 11, 1)])

class Trial:
    """A class to compute the data from each trial. Useful for fewer changes in code when changing experiment parameters."""
    
    # Defining some internal constants for the class
    _AVERAGE_MULTIPLIER = 5

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
        grating_angles_to_use=None, 
        remove_unphysical_points:bool=False, 
        background_threshold:float=0,
        custom_computer=0,):
        """Computes the efficiency vs mirror angle for the given grating angles. The provided grating angles must be explicitly present in the data.
        
        If remove_unphysical_points is True, this removes the points that have efficiencies outside the domain [0, 1]. This defaults to False.
        If background_threshold is provided, efficiencies below this number are omitted.
        If custom_computer is provided, the method runs this function instead and returns the output. This function must run taking the same parameters as this method, and must return the same type."""
        
        # If doing a custom computation, call the provided function via the following signature. Will error if not correct.
        if custom_computer:
            return custom_computer(self, grating_angles_to_use, remove_unphysical_points=remove_unphysical_points, background_threshold=background_threshold)

        # If no grating angles were explicitly provided in the method call, get all the grating angles in the data
        if grating_angles_to_use == tuple():
            grating_angles_to_use = np.unique(self.data[:, self.grating_angle_column])
        # Initialize a dictionary to return data in the form Grating angle: numpy array of powers vs. mirror angles
        result = dict()
        # Loop over grating angles
        for grating_angle in grating_angles_to_use:
            #Get a given grating angle's data
            single_run = self.data[self.data[:, self.grating_angle_column] == grating_angle]
            # Get the unique mirror angles for the specific grating angles. Warning: This sorts the array, even though it might not be sorted in the data sheet
            mirror_angles = np.unique(single_run[:, self.mirror_angle_column], axis=0)

            # Initialize a numpy array to place the averaged values for each grating angle. This initializes a 2D array with enough rows to include all mirror_angles, and with 4 columns: mirror angle, power a, power b, incident power
            avg_powers_vs_mirror_angles = np.zeros((1, 3))
            # Make this array a masked array; ie, an array that we can know which data points may be invalid
            avg_powers_vs_mirror_angles = ma.asarray(avg_powers_vs_mirror_angles)
            
            # Loop over mirror angles
            for mirror_angle in mirror_angles:
                # Get the data corresponding to a single mirror step. Warning: this assumes that the elements of the set of mirror angles in each grating angle set of data is unique.
                single_step = single_run[single_run[:, self.mirror_angle_column] == mirror_angle]
                # Get the powers
                power_a = single_step[:, self.power_a_column]
                power_b = single_step[:, self.power_b_column]
                # Average the powers
                try:
                    avg_power_a = self._average(power_a)
                except NoAveragePossibleException:
                    # set it to -1 to mark it for post-loop masking
                    avg_power_a = -1
                try:
                    avg_power_b = self._bin_average(power_b)
                except NoAveragePossibleException:
                    # set it to median
                    # avg_power_b = np.median(power_b)
                    avg_power_b = -1
                # Now stack the values into a 1x3 array and append it to avg_powers_vs_mirror_angles along the 0th axis
                element = np.column_stack((mirror_angle, avg_power_a, avg_power_b))
                avg_powers_vs_mirror_angles = np.append(avg_powers_vs_mirror_angles, element, axis=0)
            
            # Remove initialized value
            avg_powers_vs_mirror_angles = avg_powers_vs_mirror_angles[1:]
            # Mask the invalid data points in the powers (essentially marking them as known to be incorrect)
            power_a = ma.masked_equal(avg_powers_vs_mirror_angles[:, 1], -1)
            # power_b = ma.masked_equal(avg_efficiencies_vs_mirror_angles[:, 2], -1)
            # Now copy their masks, since we want a copy and not a pointer
            power_a_mask = np.copy(power_a.mask)
            # Now take average over good data points for power A and incident power
            avg_power_a = ma.average(power_a, axis=0)
            # Now substitute bad datapoints for good
            power_a[power_a_mask] = avg_power_a
            # Now reapply mask, since for some reason numpy.ma module destroys masks upon taking an average...
            power_a = ma.array(power_a, mask=power_a_mask)
            # now compute efficiency
            power_b = avg_powers_vs_mirror_angles[:, 2]
            efficiency = self.efficiency(self, power_a, power_b)
            # Now stack arrays together back into the right format
            avg_efficiencies_vs_mirror_angles = ma.column_stack((avg_powers_vs_mirror_angles[:, 0], efficiency))

            result.update(
                {
                    f"{str(grating_angle-self.grating_angle_offset)}" : avg_efficiencies_vs_mirror_angles
                }
            )
        
        return result

    def compute_efficiency_vs_grating_angle(self, 
        grating_angles_to_use,
        remove_unphysical_points:bool=False,
        background_threshold:float=0,
        custom_computer=0):
        """Computes the efficiency vs grating angle for the given grating angles. The provided grating angles must be explicitly present in the data.
        
        If remove_unphysical_points is True, this removes the points that have efficiencies outside the domain [0, 1]. This defaults to False.
        If background_threshold is provided, efficiencies below this number are omitted.
        If custom_computer is provided, the method runs this function instead and returns the output. This function runs taking the same parameters as this method, and returns the same type."""
        # if custom_computer:
        #     return custom_computer(self, grating_angles_to_use, remove_unphysical_points=remove_unphysical_points, background_threshold=background_threshold)
        
        # efficiency_vs_grating_angle = np.zeros((1, 2)) #Initialize empty array for loop; will remove this first value afterwards
        
        # for grating_angle in grating_angles_to_use:
        #     single_run = self.data[self.data[:, self.grating_angle_column] == grating_angle] #Get a given grating angle's data
        #     efficiency = np.sum(
        #         self.efficiency(
        #             self,
        #             single_run[:, self.power_a_column], 
        #             single_run[:, self.power_b_column]
        #         )
        #     ) #Compute the summed efficiencies across entire run for that grating angle
        #     efficiency_vs_grating_angle = np.append(efficiency_vs_grating_angle, [[grating_angle-self.grating_angle_offset, efficiency]], axis=0) #Add the resulting data point to the array to matrix
        
        # efficiency_vs_grating_angle = efficiency_vs_grating_angle[1:, :] #Remove the initialized value from the beginning

        # if remove_unphysical_points:
        #     efficiency_vs_grating_angle = efficiency_vs_grating_angle[efficiency_vs_grating_angle[:, 1] < 1] #Remove big outliers
        #     efficiency_vs_grating_angle = efficiency_vs_grating_angle[efficiency_vs_grating_angle[:, 1] > 0] #Remove negative outliers
        # if background_threshold:
        #     efficiency_vs_grating_angle = efficiency_vs_grating_angle[efficiency_vs_grating_angle[:, 1] > background_threshold]
        
        # return efficiency_vs_grating_angle

        # If no grating angles were explicitly provided in the method call, get all the grating angles in the data
        if grating_angles_to_use == tuple():
            grating_angles_to_use = np.unique(self.data[:, self.grating_angle_column])
        # Call the method that computes the things we want, but for each mirror angle. We know this returns a dictionary of Grating angle : efficiencies
        # Then, simply sum the efficiencies in each value of the returned dictionary.
        efficiencies_vs_mirror_angle = self.compute_efficiency_vs_mirror_angle(
            grating_angles_to_use,
            remove_unphysical_points=remove_unphysical_points,
            background_threshold=background_threshold,
            custom_computer=custom_computer
            )
        
        # Initialize array
        efficiency_vs_grating_angle = ma.zeros((1, 2))
        # Loop over data
        for grating_angle, efficiency_data in efficiencies_vs_mirror_angle.items():
            # Make it a float (since we got this from the key in a dictionary)
            grating_angle = float(grating_angle)
            # Sum efficiencies over mirror angles to get one value per grating angle
            efficiency = ma.sum(efficiency_data[:, 1], axis=0)
            element = np.column_stack((grating_angle, efficiency))
            efficiency_vs_grating_angle = np.append(efficiency_vs_grating_angle, element, axis=0)
        
        # Remove initialize value
        efficiency_vs_grating_angle = efficiency_vs_grating_angle[1:]
        return efficiency_vs_grating_angle


    def compute_powers_vs_mirror_angle(self, 
        grating_angles_to_use,
        background_threshold:float=0,
        power_scale_factor:float=1,
        custom_computer=0):
        """Computes the powers vs mirror angle for the given grating angles. The provided grating angles must be explicitly present in the data.
        
        If background_threshold is provided, powers below this number (in units of power_scale_factor) are omitted.
        If power_scale_factor is provided, the power readings will all be scaled by this factor.
        If custom_computer is provided, the method runs this function instead and returns the output. This function runs taking the same parameters as this method, and returns the same type."""
        if custom_computer:
            return custom_computer(self, grating_angles_to_use, background_threshold=background_threshold, power_scale_factor=power_scale_factor)
        
        # Initialize a dictionary to return data in the form Grating angle: numpy array of powers vs. mirror angles
        result = dict()
        # If no grating angles were explicitly provided in the method call, get all the grating angles in the data
        if grating_angles_to_use == tuple():
            grating_angles_to_use = np.unique(self.data[:, self.grating_angle_column])
        # Loop over grating angles
        for grating_angle in grating_angles_to_use:
            #Get a given grating angle's data
            single_run = self.data[self.data[:, self.grating_angle_column] == grating_angle]
            # Get the unique mirror angles for the specific grating angles. Warning: This sorts the array, even though it might not be sorted in the data sheet
            mirror_angles = np.unique(single_run[:, self.mirror_angle_column], axis=0)
            # mirror_angles = single_run[:, self.mirror_angle_column]

            # Initialize a numpy array to place the averaged values for each grating angle. This initializes a 2D array with enough rows to include all mirror_angles, and with 4 columns: mirror angle, power a, power b, incident power
            avg_powers_vs_mirror_angles = np.zeros((1, 4))
            # Make this array a masked array; ie, an array that we can know which data points may be invalid
            avg_powers_vs_mirror_angles = ma.asarray(avg_powers_vs_mirror_angles)
            
            # Loop over mirror angles
            for mirror_angle in mirror_angles:
                # Get the data corresponding to a single mirror step. Warning: this assumes that the elements of the set of mirror angles in each grating angle set of data is unique.
                single_step = single_run[single_run[:, self.mirror_angle_column] == mirror_angle]
                # Get the powers
                power_a = single_step[:, self.power_a_column]
                power_b = single_step[:, self.power_b_column]
                power_incident = self.incident_power(self, single_step[:, self.power_a_column], single_step[:, self.power_a_column])
                # Average the powers
                try:
                    avg_power_a = self._average(power_a)
                except NoAveragePossibleException:
                    # set it to -1 to mark it for post-loop masking
                    avg_power_a = -1
                try:
                    avg_power_b = self._average(power_b)
                except NoAveragePossibleException:
                    # take a median and set that instead
                    avg_power_b = np.median(power_b)
                try:
                    avg_power_incident = self._average(power_incident)
                except NoAveragePossibleException:
                    # set it to -1 to mark it for post-loop masking
                    avg_power_incident = -1
                # Now stack the values into a 1x4 array and append it to avg_powers_vs_mirror_angles along the 0th axis
                element = np.column_stack((mirror_angle, avg_power_a, avg_power_b, avg_power_incident))
                avg_powers_vs_mirror_angles = np.append(avg_powers_vs_mirror_angles, element, axis=0)
            
            # Remove initialized value
            avg_powers_vs_mirror_angles = avg_powers_vs_mirror_angles[1:]
            # Mask the invalid data points in the powers (essentially marking them as known to be incorrect)
            power_a = ma.masked_equal(avg_powers_vs_mirror_angles[:, 1], -1)
            power_b = ma.masked_equal(avg_powers_vs_mirror_angles[:, 2], -1)
            power_incident = ma.masked_equal(avg_powers_vs_mirror_angles[:, 3], -1)
            # Now copy their masks, since we want a copy and not a pointer
            power_a_mask = np.copy(power_a.mask)
            power_b_mask = np.copy(power_b.mask)
            power_incident_mask = np.copy(power_incident.mask)
            # Now take average over good data points for power A and incident power
            avg_power_a = ma.average(power_a, axis=0)
            avg_power_incident = ma.average(power_incident, axis=0)
            # Now substitute bad datapoints for good
            power_a[power_a_mask] = avg_power_a
            power_incident[power_incident_mask] = avg_power_incident
            # Now reapply mask, since for some reason numpy.ma module destroys masks upon taking an average...
            power_a = ma.array(power_a, mask=power_a_mask)
            power_incident = ma.array(power_incident, mask=power_incident_mask)
            # Now stack arrays together back into the right format
            avg_powers_vs_mirror_angles = ma.column_stack((avg_powers_vs_mirror_angles[:, 0], power_a, power_b, power_incident))
            # Save mask and copy as normal array to get power multiplier factor
            mask = np.copy(avg_powers_vs_mirror_angles.mask)
            avg_powers_vs_mirror_angles = np.asarray(avg_powers_vs_mirror_angles)
            # multiply the datapoints by the power_scale_factor
            avg_powers_vs_mirror_angles *= power_scale_factor
            # Divide by the same factor for the mirror angles row to account for the fact that we don't scale angles
            avg_powers_vs_mirror_angles[:, 0] /= power_scale_factor
            avg_powers_vs_mirror_angles = ma.array(avg_powers_vs_mirror_angles, mask=mask)

            result.update(
                {
                    f"{str(grating_angle-self.grating_angle_offset)}" :avg_powers_vs_mirror_angles
                }
            )
        
        return result
    
    def _average(self, power:np.ndarray):
        """Private method to compute the average power. If the power is bad even after doing the succeeding averages, then a custom exception is raised (NoAveragePossibleException)."""
        # Compute the first average power
        first_average = np.average(power, axis=0)
        # Select power values that are less than 5 times the first average
        power = power[power < first_average*self._AVERAGE_MULTIPLIER]
        # Select power values that are greater than 1/5 the first average
        power = power[power > first_average*1/self._AVERAGE_MULTIPLIER]
        # If the last conditional slice resulted in 0 power readings that were close to the first average
        if len(power) == 0:
            raise NoAveragePossibleException
        # Return the final average. This assumes that the previous steps removed the extremal values
        return np.average(power, axis=0)
    
    def _bin_average(self, power: np.ndarray):
        """Private method to compute the power in cases where we have 1 (maybe 2) outliers that are order of magnitude from the rest. Essentially this is taking the mode and then averaging the most frequent values."""
        # Map the power to the bin it resides in. Bins are specified via BIN_AVERAGE_BINS
        digits = np.digitize(power, BIN_AVERAGE_BINS)
        # Find the most frequent bin. This assumes there is only one most frequent bin.
        unique_bins, counts = np.unique(digits, return_counts=True)
        most_frequent_bin = unique_bins[np.argmax(counts)]
        # Get the most frequent bin powers
        most_frequent_powers = power[digits == most_frequent_bin]
        # If there are no most frequent powers, raise NoAveragePossibleException. Otherwise, return the average power
        if len(most_frequent_powers) == 0:
            raise NoAveragePossibleException
        return np.average(most_frequent_powers)
        
        


def default_horizontal_incident_power(trial: Trial, power_a, power_b):
    """Default incident power function. Assumes power sensor A is measuring the reflected power off the slide. This uses the first value for power sensor A in the entire trial, since power sensor A is faulty"""
    reflectivity = trial.slide_coefficients.loc["A"]["RH"] # Get the reflection coefficient for sensor A
    return (power_a - trial.sensor_a_background)/reflectivity

def default_vertical_incident_power(trial: Trial, power_a, power_b):
    """Default incident power function. Assumes power sensor A is measuring the reflected power off the slide. This uses the first value for power sensor A in the entire trial, since power sensor A is faulty"""
    reflectivity = trial.slide_coefficients.loc["A"]["RV"] # Get the reflection coefficient for sensor A
    return (power_a - trial.sensor_a_background)/reflectivity

def default_horizontal_efficiency(trial: Trial, power_a, power_b):
    """Default efficiency function. This uses the first value for power sensor A in the entire trial, since power sensor A is faulty"""
    reflectivity = trial.slide_coefficients.loc["A"]["RH"]
    power_a_mask = np.copy(power_a.mask)
    power_a = np.array(power_a)
    power_b = np.array(power_b)
    result = (power_b-trial.sensor_b_background)/(((power_a - trial.sensor_a_background)/reflectivity) - (power_a - trial.sensor_a_background))
    # Now reapply mask, since for some reason numpy.ma module destroys masks upon taking an average...
    result = ma.array(result, mask=power_a_mask)
    # power_a = np.broadcast_to(np.array([trial.data[0, trial.power_a_column]]), power_b.shape)
    return result

def default_vertical_efficiency(trial: Trial, power_a, power_b):
    """Default efficiency function. This uses the first value for power sensor A in the entire trial, since power sensor A is faulty"""
    reflectivity = trial.slide_coefficients.loc["A"]["RV"]
    power_a_mask = np.copy(power_a.mask)
    power_a = np.array(power_a)
    power_b = np.array(power_b)
    result = (power_b-trial.sensor_b_background)/(((power_a - trial.sensor_a_background)/reflectivity) - (power_a - trial.sensor_a_background))
    # Now reapply mask, since for some reason numpy.ma module destroys masks upon taking an average...
    result = ma.array(result, mask=power_a_mask)
    # power_a = np.broadcast_to(np.array([trial.data[0, trial.power_a_column]]), power_b.shape)
    return result
class NoAveragePossibleException(Exception):
    """An exception to be raised when no sequential average is possible."""
    pass
