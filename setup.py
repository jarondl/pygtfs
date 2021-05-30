import codecs
import os.path

from setuptools import setup, find_packages

readme = os.path.join(os.path.dirname(__file__), 'README.md')
with codecs.open(readme, encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pygtfs',
    author='Yaron de Leeuw',
    author_email="me@jarondl.net",
    description='Models GTFS data in a database.',
    long_description=long_description,
    license='MIT',
    keywords='gtfs',
    url='https://github.com/jarondl/pygtfs',
    packages=find_packages(),
    install_requires=['sqlalchemy>=0.7.8',
                      'pytz>=2012d',
                      'six',
                      'docopt'
                      ],
    tests_require=['nose'],
    test_suite='nose.collector',
    setup_requires=['setuptools_scm'],
    use_scm_version={'write_to': os.path.join('pygtfs', '_version.py')},
    entry_points={'console_scripts': ['gtfs2db = pygtfs.gtfs2db:main']},
    classifiers=[
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        ]
)
