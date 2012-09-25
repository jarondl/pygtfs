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

The Schedule object represents a collection of objects that correspond to the contents of a GTFS feed. You can get the list of agencies, stops, routes, etc. with fairly straightforwardly named attributes (see "Reference" below for full details):

    >>> sched.agencies
    [<Agency BART: Bay Area Rapid Transit>, <Agency AirBART: AirBART>]
    >>> sched.routes
    [<Route AirBART: >, <Route 01: >, <Route 03: >, <Route 05: >, <Route 07: >, <Route 11: >]

For GTFS entities that are identified by a dataset-unique identifier, you can also use the above attributes with `_by_id` appended to get a dictionary keyed on that identifier. So for example: 

    >>> sched.agencies_by_id
    {u'AirBART': <Agency AirBART: AirBART>, u'BART': <Agency BART: Bay Area Rapid Transit>}
    >>> sched.stops_by_id['SFIA']
    <Stop SFIA: San Francisco Int'l Airport>

The GTFS entity objects have attributes that correspond in name to the field definitions in the [GTFS reference](https://developers.google.com/transit/gtfs/reference). 

    >>> sched.stops_by_id['SFIA'].stop_name
    u"San Francisco Int'l Airport"
    >>> sched.routes[1].route_long_name
    u'Pittsburg/Bay Point - SFIA/Millbrae'

GTFS entities which cross-reference each other can also be obtained straightforwardly with attributes (again, see "Reference" below for full details):

    >>> sched.trips_by_id['01SFO10'].service  # the service associated with trip 01SFO10
    <Service WKDY (MTWThFSSu)>

Reference
---------

(to be populated with documentation when I'm not on an airplane that's about to land, sorry in the meantime look at `schedule.py` for the properties of Schedule and `entity/unmapped_entities.py` for the definitions of GTFS entity classes like Agency, Service, Stop, etc.)

To-do
-----

- Complete documentation in reference section
- Can I easily return a dictionary of backreferenced values rather than a list? (so for example sched.trips_by_id.stop_times_by_id)?
- Improve testing; add some unit testing framework and test with a variety of GTFS data feeds. At this point I've only done some testing-by-hand with a few transit systems: MTA subway, MTA Manhattan buses, BART. 
