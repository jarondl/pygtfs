gtfs-sql
========

Overview
--------

Latest version: 0.1a1

gtfs-sql is a library that reads and models information stored in Google's [General Transit Feed Specification (GTFS)](https://developers.google.com/transit/) format. GTFS is a format designed to specify information about a transit system, such as a city's subways or a private company's bus services. gtfs-sql stores information in an SQLite database using SQLAlchemy to facilitate the storage of Python objects in a relational database. 

gtfs is a fork of bmander's gtfs. Although they are very similar, I changed some of the variable names and conventions, so you shouldn't expect them to be precisely "compatible" with each other. 

License: MIT, included in `license.txt`. The original gtfs code did not include any license information; I always specify licenses out of habit; MIT is a fairly permissive license in any case. 

Dependencies
------------

- [SQLAlchemy](http://www.sqlalchemy.org/) - I used version 0.7.8. SQLAlchemy is used to map GTFS entities like Agency, Stop, Route, Service, etc. into a database. If you want to read the code it will help a lot to know SQLAlchemy (in fact this project was my introduction to it). 
- [pytz](http://pytz.sourceforge.net/) - I used version 2012d. A few GTFS fields are expected to be in a [tz time zone format](http://en.wikipedia.org/wiki/List_of_tz_database_time_zones). 

Installation
------------

Clone the repo and use `python setup.py install`. At some point I may add this to PyPI, but I don't think it's mature enough. 

Basic usage
-----------

To include gtfs-sql functionality in your application, use `import gtfs`. 

If you have GTFS data either as a zip file or as a collection of files in a folder, you can load the data into an in-memory SQLite database and into a Schedule variable as follows (using [BART](http://www.bart.gov/) data as an example): 

    sched = gtfs.load('data/bart.zip')
    sched = gtfs.load('data/bart/')

You can load the data into an SQLite database on disk as well by passing a second argument to `load`. 

    sched = gtfs.load('data/bart.zip', 'data/bart.db')

Once you've created the database you can access the data quickly without regenerating the database by creating a Schedule object directly. 

    sched = gtfs.Schedule('data/bart.db')

The Schedule object represents a collection of objects that correspond to the contents of a GTFS feed. You can get the list of agencies, stops, routes, etc. with some fairly straightforwardly named attributes (see `schedule.py` for the full list):

    >>> sched.agencies
    [<Agency BART: Bay Area Rapid Transit>, <Agency AirBART: AirBART>]
    >>> sched.routes
    [<Route AirBART: >, <Route 01: >, <Route 03: >, <Route 05: >, <Route 07: >, <Route 11: >]

Once you've got the data in a variable, you can get objects corresponding to the GTFS data, which in turn have attributes that correspond in name to the field definitions in the [GTFS reference](https://developers.google.com/transit/gtfs/reference). 

    >>> sched.stops[0]
    <Stop 12TH: 12th St. Oakland City Center>
    >>> sched.routes[1].route_long_name
    u'Pittsburg/Bay Point - SFIA/Millbrae'

Some of the attributes are also cross-referenced: 

    >>> sched.routes[1].trips[0].stop_times[0].stop
    <Stop PITT: Pittsburg/Bay Point>

To-do
-----

- For entities uniquely identified by an id, add decorators that return a dictionary mapping ids to objects. 
- Add some more backrefs, including for optional fields; just generally go through GTFS and ensure that all cross-references are set up as desired
- Improve testing; add some unit testing framework and test with a variety of GTFS data feeds. At this point I've only done some testing-by-hand with a few transit systems: MTA subway, MTA Manhattan buses, BART. 
