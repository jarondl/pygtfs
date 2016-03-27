from setuptools import setup, find_packages
setup(
    name='pygtfs',
    version="0.1.2",
    author='Yaron de Leeuw',
    description='Models GTFS data in a database.',
    license='MIT',
    keywords='gtfs',
    url='https://github.com/jarondl/pygtfs',
    packages = find_packages(),
    install_requires=['sqlalchemy>=0.7.8',
                      'pytz>=2012d',
                      'six',
                      'docopt'
                     ],
    entry_points = {'console_scripts': ['gtfs2db = pygtfs.gtfs2db:main']},
    classifiers = [
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3"
        ]
)
