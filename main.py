"""This is simply a convenience module to easily call the CLI from the project root directory. May consider wrapping this into a usual shell command using setuptools."""
import cli.plotdata as plotdata

if __name__ == "__main__":
    plotdata.main()