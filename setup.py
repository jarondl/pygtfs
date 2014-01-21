from setuptools import setup, find_packages
setup(
    name='pytgtfs',
    version='0.1.0',
    author='Yaron de Leeuw',
    description='Models GTFS data and saves it to/reads it from a database.',
    license='MIT',
    keywords='gtfs',
    url='https://github.com/jarondl/pygtfs',
    packages = find_packages(),
    install_requires=['sqlalchemy>=0.7.8',
                      'pytz>=2012d',
                     ],
    entry_points = {'console_scripts': ['gtfs2db = pygtfs.gtfs2db:main']}
)
