from setuptools import setup, find_packages
setup(
    name = "gtfs",
    version = "0.1",
    packages = find_packages(),
    install_requires=['sqlalchemy>=0.6.3'],
    entry_points = {
      "console_scripts": ["compile_gtfs = gtfs.scripts.compile_gtfs:main"]
    }
)
