pygtfs
========

Overview
--------

Latest version: 0.1.0

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
clone the repo, and use `python setup.py install`. At some point I may add this
to PyPI, but I don't think it's mature enough yet. 

Basic usage
-----------

To include pygtfs functionality in your application, use `import pygtfs`. 

The first thing you need to to is to create a new schedule object:

    sched = pygtfs.Schedule(":memory:")

This will create an in memory sqlite database. Instead you can supply a
filename to be used for sqlite (such as ('gtfs.sqlite'), or a sqlalchemy
database connection.

Then you can load gtfs feeds into the databas, by using append:

    pygtfs.append_feed(sched, "sample-gtfs-feed.zip")

Where the gtfs feed can be either a `.zip` file, or a folder full of `.txt` files.
You can add as many feeds as you want into a single database, without fear
of conflicts (but you can two stop names for one place, one from each feed for example).
Another option to load feeds is to use the 'gtfs2db' script as explained later.

The Schedule object represents a collection of objects that correspond to the
contents of a GTFS feed. You can get the list of agencies, stops, routes, etc.
with fairly straightforwardly named attributes (see "Reference" below for full details):

    >>> sched.agencies
    [<Agency BART: Bay Area Rapid Transit>, <Agency AirBART: AirBART>]
    >>> sched.routes
    [<Route AirBART: >, <Route 01: >, <Route 03: >, <Route 05: >, <Route 07: >, <Route 11: >]

For GTFS entities that are identified by a dataset-unique identifier, there is
also a function to get them by id: 

    >>> sched.agencies_by_id('AirBART')
    [<Agency AirBART: AirBART>]
    >>> sched.stops_by_id('SFIA')
    [<Stop SFIA: San Francisco Int'l Airport>]

The GTFS entity objects have attributes that correspond in name to the field
definitions in the [GTFS reference](https://developers.google.com/transit/gtfs/reference). 

    >>> sched.stops_by_id('SFIA')[0].stop_name
    u"San Francisco Int'l Airport"
    >>> sched.routes[1].route_long_name
    u'Pittsburg/Bay Point - SFIA/Millbrae'

GTFS entities which cross-reference each other can also be obtained straightforwardly with attributes (again, see "Reference" below for full details):

    >>> sched.trips_by_id('01SFO10').service  # the service associated with trip 01SFO10
    <Service WKDY (MTWThFSSu)>

gtfs2db
-------

`setup.py install` will also install a command-line script `gtfs2db` that takes a GTFS zip file or directory as an argument and will load the data into a database usable with pygtfs. Run `gtfs2db --help` for more. 

Reference
---------

### Schedule

A `Schedule` object represents all of the data contained in a GTFS feed. Schedule properties that return GTFS data in array form: 

- `schedule.agencies`
- `schedule.stops`
- `schedule.routes`
- `schedule.services`
- `schedule.service_exceptions`
- `schedule.trips`
- `schedule.stop_times`
- `schedule.fares`
- `schedule.fare_rules`
- `schedule.shape_points`
- `schedule.frequencies`
- `schedule.transfers`
- `schedule.feed_info`

Schedule properties that return a dictionary of GTFS data keyed on their unique identifier: 

- `schedule.agencies_by_id`
- `schedule.stops_by_id`
- `schedule.routes_by_id`
- `schedule.services_by_id`
- `schedule.trips_by_id`
- `schedule.fares_by_id`
- `schedule.shape_points_by_id`

### GTFS entities

The following classes correspond to entities found in GTFS data. All the entities have attributes that correspond to data items in the [GTFS reference](https://developers.google.com/transit/gtfs/reference). For example, an `Agency` object has attributes `Agency.agency_id`, `Agency.agency_name`, etc. They will be returned in the appropriate type: integer, boolean, float, `pytz` timezone object, etc. `Service` and `ServiceException` correspond to the `calendar.txt` and `calendar_dates.txt` files, respectively. 

- `Agency`
- `Stop`
- `Route`
- `Service`
- `ServiceException`
- `Trip`
- `StopTime`
- `Fare`
- `FareRule`
- `ShapePoint`
- `Frequency`
- `Transfer`
- `FeedInfo`

In addition to the GTFS attributes, some additional attributes are available that return entities that are mapped to the entity in question via a relationship, either a single entity, a list, or a dictionary by unique id: 

- `Agency.routes`
- `Agency.routes_by_id`
- `Stop.stop_times`
- `Stop.transfers_to`
- `Stop.transfers_from`
- `Route.agency`
- `Route.trips`
- `Route.fare_rules`
- `Service.service_exceptions`
- `Service.trips`
- `ServiceException.service`
- `Trip.route`
- `Trip.service`
- `Trip.stop_times`
- `Trip.frequencies`
- `StopTime.stop`
- `StopTime.trip`
- `Fare.fare_rules`
- `FareRule.fare`
- `FareRule.route`
- `Frequency.trip`
- `Transfer.from_stop`
- `Transfer.to_stop`

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
