"""A module containing the possible errors when extracting trial information from trial folders."""


class InvalidPolarizationState(Exception):
    """Error to be raised if an invalid polarization is parsed."""
    pass


class GratingParameterFileError(Exception):
    """Error to be raised if there is an error reading grating_parameters.csv file."""
    pass


class MissingGratingParameters(Exception):
    """Error to be raised if there are missing parameters in the grating_parameters.csv file."""
    pass
