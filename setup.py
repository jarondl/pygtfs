from setuptools import setup, find_packages
from pygtfs import __version__

setup(
    name='pygtfs',
    version=__version__,
    author='Yaron de Leeuw',
    description='Models GTFS data in a database.',
    license='MIT',
    keywords='gtfs',
    url='https://github.com/jarondl/pygtfs',
    packages=find_packages(),
    install_requires=['sqlalchemy>=0.7.8',
                      'pytz>=2012d',
                      'six',
                      'docopt'
                      ],
    test_require=['nose'],
    test_suite='nose.collector',
    entry_points={'console_scripts': ['gtfs2db = pygtfs.gtfs2db:main']},
    classifiers=[
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
        ]
)
