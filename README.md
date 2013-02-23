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

- [SQLAlchemy](http://www.sqlalchemy.org/) 0.7.8. Used for all mapping of GTFS objects to the relational DB. You'll need to be familiar with it to read the code; the [documentation](http://docs.sqlalchemy.org/) is pretty solid. 
- [pytz](http://pytz.sourceforge.net/) 2012d. A few GTFS fields are expected to be in a [tz time zone format](http://en.wikipedia.org/wiki/List_of_tz_database_time_zones). 

Installation
------------

Get [setuptools](http://pypi.python.org/pypi/setuptools) if you don't have it, clone the repo, and use `python setup.py install`. At some point I may add this to PyPI, but I don't think it's mature enough yet. 

Basic usage
-----------

To include gtfs-sql functionality in your application, use `import gtfs`. 

If you have GTFS data either as a zip file or as a collection of files in a folder, you can load the data into an in-memory SQLite database and into a Schedule variable as follows (using [BART](http://www.bart.gov/) data as an example): 

    sched = gtfs.load('data/bart.zip')
    sched = gtfs.load('data/bart/')

You can load the data into an SQLite database on disk as well by passing a second argument to `load`. 

    sched = gtfs.load('data/bart.zip', 'data/bart.db')

Once you've created the database you can access the data quickly without regenerating the database by creating a Schedule object directly as follows. Keep in mind that the SQL database will be much bigger on disk than a zip file (the order of magnitude varies a decent amount). 

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

gtfs2db
-------

`setup.py install` will also install a command-line script `gtfs2db` that takes a GTFS zip file or directory as an argument and will load the data into a database usable with gtfs-sql. Run `gtfs2db --help` for more. 

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

All these classes inherit from the abstract `Entity` class and define the following attributes/methods: 

- `Entity.table_name` - name of the table that stores this entity in the database, and, when appended with '.txt', the name of the GTFS file containing this information. 
- `Entity.gtfs_required` - whether the GTFS file corresponding to this entity is required or not. Both `calendar.txt` and `calendar_dates.txt` are considered not required, although one of them must be present. 
- `Entity.fields` - list of Fields, although not something you generally need to refer to; used to construct tables/mappings
- `Entity.check_mandatory_fields()` - verifies whether all Fields flagged as mandatory are present (does not necessarily check their validity though, which is done in the constructors). Called in the base `Entity` constructor. 

`Entity.metadata` (specifically that of the base class `Entity`) is the metadata used to control all of the SQLAlchemy mappings. 

### Feed and loading

`load(feed_filename, db_connection=":memory:", strip_fields=True, commit_chunk=500)`

`load` loads the GTFS data at `feed_filename`, which can either be a zip file or a directory containing GTFS CSV files. `db_connection` can be used to tell gtfs-sql to persist the data to disk, rather than storing it temporarily in memory. It can be either a full database uri e.g. "postgresql://postgres@localhost:5432/gtfs" or a filename for SQLite. The default name `:memory:` is a SQLAlchemy special word that corresponds to an in-memory database. 

If `strip_fields` is true each entry will have leading/trailing blanks stripped. `commit_chunk` controls how many SQL transactions are added to each database session before being committed. 

The `Feed` and `CSV` classes are used internally by `load`. 

### Table generation and mapping

The functions in `map_entities.py`, `table_def_from_entity()` and `create_and_map_tables()`, are run when gtfs-sql is imported, but are not needed otherwise. They construct tables and mappings based on the contents of `Entity.fields` plus a few extra parameters denoting relationships. I won't go into detail on them because they are not needed to use gtfs-sql.  

To-do
-----

- Improve testing; add some unit testing framework and test with a variety of GTFS data feeds. 
