gtfs
====

Overview
--------

gtfs is a library that reads and models information stored in Google's [General Transit Feed Specification (GTFS)](https://developers.google.com/transit/) format. GTFS is a format designed to specify information about a transit system, such as a city's subways or a private company's bus services. gtfs stores information in a local SQLite database using SQLAlchemy. 

gtfs is a fork of bmander's gtfs. Although the code is heavily derivative of bmander's gtfs, some of the variable names and conventions are different and so you shouldn't expect them to be compatible. 

License: MIT, included in license.txt. bmander's code did not include any license information; MIT is a fairly permissive license in any case. 

Dependencies
------------

SQLAlchemy
pytz
