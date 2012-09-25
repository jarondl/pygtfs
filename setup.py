from setuptools import setup, find_packages
setup(
    name='gtfs-sql',
    version='0.1a1',
    author='Andrew Lim',
    description='Models GTFS data and saves it to/reads it from a database.',
    license='MIT',
    keywords='gtfs',
    url='https://github.com/andrewblim/gtfs-sql',
    packages = find_packages(),
    install_requires=['sqlalchemy>=0.7.8',
                      'pytz>=2012d',
                     ],
    entry_points = {'console_scripts': ['gtfs2db = gtfs.gtfs2db:main']}
)
