pygtfs
========

[![Travis](https://img.shields.io/travis/jarondl/pygtfs/master.svg?style=flat-square)](https://travis-ci.org/jarondl/pygtfs)
[![PyPI](https://img.shields.io/pypi/v/pygtfs.svg)](https://pypi.python.org/pypi/pygtfs)


Overview
--------

pygtfs is a library that models information stored in Google's
[General Transit Feed Specification (GTFS)](https://developers.google.com/transit/)
format. GTFS is a format designed to specify information about a transit
system, such as a city's subways or a private company's bus services. pygtfs
stores information in an SQLite database using SQLAlchemy to facilitate the
storage of Python objects in a relational database. 

pygtfs is a fork of @eoghanmurray's fork of a @andrewblim's gtfs-sql which is
a fork of @bmander's gtfs. See the git logs for more fun history.

License: MIT, included in `license.txt`.


Dependencies
------------

- [SQLAlchemy](http://www.sqlalchemy.org/) 0.7.8. Used for all mapping of GTFS
  objects to the relational DB. You'll need to be familiar with it to read the
  code; the [documentation](http://docs.sqlalchemy.org/) is pretty solid. 
- [pytz](http://pytz.sourceforge.net/) 2012d. A few GTFS fields are expected
  to be in a [tz time zone format](http://en.wikipedia.org/wiki/List_of_tz_database_time_zones). 
- [six](http://pythonhosted.org/six/). Used in order to support python2 and
  python3 in a single code base.
- [docopt](http://docopt.org/). Pythonic command line arguments parser, that
  will make you smile

Installation
------------

Get [setuptools](http://pypi.python.org/pypi/setuptools) if you don't have it,
clone the repo, and use `python setup.py install`.

Documentation
-------------
Hosted on https://pygtfs.readthedocs.org/

TODO
-----

- Improve testing; add some unit testing framework and test with a variety of GTFS data feeds. 
- Add more docs

Why fork?
--------------
- natively support several gtfs feeds per database
- less SLOC, more DRY
- add python3 support
- renamed to a more generic name
- will continue to maintain
