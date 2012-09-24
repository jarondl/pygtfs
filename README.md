gtfs
====

Overview
--------

Version: 0.1a

gtfs is a library that reads and models information stored in Google's [General Transit Feed Specification (GTFS)](https://developers.google.com/transit/) format. GTFS is a format designed to specify information about a transit system, such as a city's subways or a private company's bus services. gtfs stores information in a local SQLite database using SQLAlchemy. 

gtfs is a fork of bmander's gtfs. Although the code is strongly derivative of bmander's gtfs, some of the variable names and conventions are different. 

License: MIT, included in license.txt. bmander's code did not include any license information; MIT is a fairly permissive license in any case. 

Dependencies
------------

- [SQLAlchemy](http://www.sqlalchemy.org/) - I used version 0.7.8
- [pytz](http://pytz.sourceforge.net/) - I used version 2012d

Installation
------------

(still to-do)

Usage
-----

To include gtfs functionality in your application, use `import gtfs`. 

    sched = gtfs.load('data/bart.zip')

This will load the GTFS data in `bart.zip` into an in-memory SQLite database and will store the GTFS data in the variable `sched`. This may take some time if the GTFS data is large. 

    sched = gtfs.load('data/bart/')

GTFS files are commonly distributed as zip files so it's convenient to leave them that way, but you can also load a directory containing the GTFS CSV files. 

    sched = gtfs.load('data/bart.zip', 'data/bart.db')

You can load the data into an SQLite database on disk as well (if it's not there it will be created). This is useful because once you've created the database you can later access the data much more quickly with: 

    sched = gtfs.Schedule('data/bart.db')

Once you've got the data in a variable, you can get objects corresponding to the GTFS data, which in turn have attributes that correspond in name to the field definitions in the [GTFS reference](https://developers.google.com/transit/gtfs/reference). 

    >>> sched.agencies
    [<Agency BART: Bay Area Rapid Transit>, <Agency AirBART: AirBART>]
    >>> sched.stops[0]
    <Stop 12TH: 12th St. Oakland City Center>
    >>> sched.routes[1].route_long_name
    u'Pittsburg/Bay Point - SFIA/Millbrae'

Some of the attributes are also cross-referenced: 

    >>> sched.routes[1].trips[0].stop_times[0].stop
    <Stop PITT: Pittsburg/Bay Point>

To-do
-----

- Add some more backrefs, including for optional fields; just generally go through GTFS and ensure that all cross-references are set up as desired
- Improve testing; add some unit testing framework and test with a variety of GTFS data feeds. At this point I've only done some testing-by-hand with a few transit systems: MTA subway, MTA Manhattan buses, BART. 
- Improve this documentation file
- Rename this project - I think something like gtfs-sql is a more fitting name
- Double check setup.py, scripts/, and test/, which I haven't looked at yet
