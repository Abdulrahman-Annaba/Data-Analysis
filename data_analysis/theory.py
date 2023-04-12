import numpy as np

class Grating:

    def __init__(self, groove_spacing:int=1200, e_m:float=-46.6, wavelength: float=640, e_d:float=1, epsilon:float=1):
        """Creates a grating object.
        
        :param groove_spacing: the number of grooves per millimeter in the grating.
        :param e_m: the dielectric constant of the grating material.
        :param wavelength: the wavelength of the incoming light, in nanometers.
        :param e_d: the dielectric constant of the other medium at the grating interface.
        :param epsilon: the angle that the plane of incidence makes with the grating normal, in degrees. Positive values indicate a decline.
        """
        self.groove_spacing = groove_spacing
        self.e_m = e_m
        self.wavelength = wavelength
        self.e_d = e_d
        self.epsilon = epsilon

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
    
    def spr_angles(self, n_orders:int):
        """Computes the incident angles where maximal SPR occurs up to n_orders.
        
        :param n_orders: the total number of orders to consider. This is halved to account for the negative orders.
        :return: a dictionary of order numbers and angles in degrees where maximal SPR can occur."""

        orders = divmod(n_orders, 2)[0]
        constraint = ((self.e_d*self.e_m)/(self.e_d + self.e_m))**(1/2)
        wavelength = self.wavelength*10**-9
        groove_spacing = self.groove_spacing*10**3

        result = dict()
        for m in range(-orders, orders + 1, 1):
            incident_angle = np.arcsin(constraint - m*wavelength*groove_spacing)*180/np.pi
            if incident_angle <= 90 and incident_angle >= -90:
                result.update({str(m): incident_angle})
        flipped_results = dict()
        for order, angle in result.items():
            flipped_results.update({str(-1*int(order)) : -1*angle})
        result.update(flipped_results)
        return result
    
    def woods_anomaly_angles(self, n_orders: int):
        """Computes the incident angles at which wood's anomaly occurs, according to the equation sin(incident_angle) = m*wavelength*groove_spacing/cos(epsilon) +/- 1, where epsilon is the angle between the grating normal and the plane of incidence in degrees.
        
        :param n_orders: the total number of orders to consider. This is halved to account for the negative orders.
        :return: a dictionary of order numbers and incident angles representing the locations of wood's anomalies."""
        orders = divmod(n_orders, 2)[0]
        wavelength = self.wavelength*10**-9
        groove_spacing = self.groove_spacing*10**3
        epsilon = self.epsilon * np.pi/180

        result = dict()
        for m in range(-orders, orders + 1, 1):
            incident_angle = np.arcsin(m*wavelength*groove_spacing/np.cos(epsilon) + 1) * 180/np.pi
            if incident_angle <= 90 and incident_angle >= -90:
                result.update({str(m): incident_angle})
        return result

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
    wavelength = 637.3
    epsilon = 3.8914
    groove_spacing = 1200

    e_m = -56.96
    e_d = 1.00**2
    grating = Grating(groove_spacing, e_m, wavelength, e_d, epsilon)

    print(grating.spr_angles(10))

    print(grating.woods_anomaly_angles(10))
