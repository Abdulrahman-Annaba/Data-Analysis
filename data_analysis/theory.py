import numpy as np

class Grating:

    def __init__(self, groove_spacing:int=1200):
        """Creates a grating object.
        
        :param groove_spacing: the number of grooves per millimeter in the grating."""
        self.groove_spacing = groove_spacing
    
    def find_diffraction_orders(
        self,
        wavelength:float,
        incident_angle:float,
        epsilon:float
    ):
        """Given state parameters, this method uses the grating equation to compute locations of different diffraction orders.
        
        Parameters:
        :param wavelength: the wavelength of the input light in nanometers.
        :param incident_light_angle: the angle at which the input light strikes the grating in the plane of incidence, measured from the grating normal in degrees.
        :param epsilon: the pitch of the grating normal relative to the input light in degrees.
        :return: a numpy array of diffraction order angles."""
        
        # Convert parameters to SI units
        wavelength = wavelength*10**-9
        groove_spacing = self.groove_spacing*10**3
        epsilon = epsilon*np.pi/180
        incident_angle = incident_angle*np.pi/180
        # First find the possible values of m, the diffraction order integer

        # Assumption: there will be no diffraction orders greater than 5 or less than -5
        possible_m = np.arange(-5, 6, 1)

        result = self._constrained_function(groove_spacing, wavelength, epsilon, incident_angle, possible_m)
        # Orders with the constraint less than -2 or greater than 2 are not physical, therefore we exclude them
        result = result[result >= -1]
        result = result[result <= 1]

        # Diffraction orders from valid possible m
        diffraction_orders = self._m(groove_spacing, wavelength, epsilon, incident_angle, result)

        # Compute the angles of the diffraction orders, measured from the normal of the diffraction grating in degrees
        diffraction_order_angles = self._diffraction_order_angle(groove_spacing, wavelength, epsilon, incident_angle, diffraction_orders)
        # Return the diffraction orders and their corresponding angles
        return (diffraction_orders, diffraction_order_angles)
    
    @staticmethod
    def _constrained_function(groove_spacing, wavelength, epsilon, incident_angle, m):
        return (groove_spacing*wavelength*1/np.cos(epsilon)*m - np.sin(incident_angle))
    
    @staticmethod
    def _m(groove_spacing, wavelength, epsilon, incident_angle, constraint):
        return ((constraint + np.sin(incident_angle))*np.cos(epsilon)/(groove_spacing*wavelength))

    @staticmethod
    def _diffraction_order_angle(groove_spacing, wavelength, epsilon, incident_angle, m):
        return np.arcsin(groove_spacing*wavelength*m/np.cos(epsilon) - np.sin(incident_angle)) * 180/np.pi
    

if __name__ == "__main__":
    """Example usage"""
    incident_angle = 90
    wavelength = 640
    epsilon = (17.80*10**-3)/(24.5*10**-2)*180/np.pi
    groove_spacing = 1200

    grating = Grating(groove_spacing)

    (orders, angles) = grating.find_diffraction_orders(wavelength, incident_angle, epsilon)
    print(orders, angles)
