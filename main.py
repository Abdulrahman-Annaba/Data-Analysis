"""This is simply a convenience module to easily call the CLI from the project root directory. May consider wrapping this into a usual shell command using setuptools."""
import cli.plotdata as plotdata
import sys


class InvalidPythonVersion(Exception):
    """Raised when the python version is below the minimum supported value."""


if __name__ == "__main__":
    if not (sys.version_info.major > 3 and sys.version_info.minor > 10):
        raise InvalidPythonVersion(
            "Python version 3.10 or higher is required to run this CLI.")
    plotdata.main()
