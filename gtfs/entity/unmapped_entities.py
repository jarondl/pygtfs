from sqlalchemy import Table, MetaData, Column, ForeignKey, ForeignKeyConstraint
from sqlalchemy import String, Unicode, Integer, Float, Boolean, Date, Interval, PickleType
import datetime
import pytz
import re

def int_hex(x):
    return int(x, 16)
    
def date_yyyymmdd(x):
    return datetime.datetime.strptime(x, '%Y%m%d').date()

def timedelta_hms(x):
    (hours, minutes, seconds) = map(int, re.split(':', x))
    return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

class Field(object):
    """Represents an attribute to store in the database. An Entity object is
    associated with an array of Fields in Entity.fields. Like SQLAlchemy's 
    Column() but with some extra fields: 
    
    - name: column name
    - column_type: SQLAlchemy column type, such as String, Integer, etc.
    - foreign_key: name of foreign key (the name of a field in the table, like
      tablename.field, not a call to ForeignKey() itself) (default None)
    - primary_key: whether this field is a primary key or not (default False)
    - cast: a function to call on the field when instantiating the Entity, to
      convert its type to the appropriate value (default None, no cast)
    - mandatory: is this field's presence mandatory in GTFS? (default False)
    - default: if this field is omitted or a blank string, what is the default 
      value? (default None)
    """
    def __init__(self, name, column_type, foreign_key=None, primary_key=False,
                 cast=None, mandatory=False, default=None):
        self.name = name
        self.column_type = column_type
        self.foreign_key = foreign_key
        self.primary_key = primary_key
        self.cast = cast
        self.mandatory = mandatory
        self.default = default

class EntityMissingFieldError(Exception):
    """Raised when a subclass of Entity is instantiated without mandatory fields."""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class EntityBadFieldError(Exception):
    """Raised when a subclass of Entity is instantiated with improper values."""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Entity(object):
    """Represents the base class of objects to be stored by SQLAlchemy. 
    An Entity is associated with an array of Field objects. Entities are 
    unmapped, mapping is done separately via the "classical" method 
    (declarative being in my opinion a bigger pain to implement here).
    """
    
    metadata = MetaData()
    
    table_name = None
    gtfs_required = None
    fields = []
    
    def __init__(self, **kwargs):
        for field in self.fields:
            if field.name in kwargs:
                field_value = kwargs[field.name]
                if field_value == '':
                    setattr(self, field.name, field.default)
                elif field_value is not None and field.cast is not None:
                    setattr(self, field.name, field.cast(field_value))
                else:
                    setattr(self, field.name, field_value)
            else:
                setattr(self, field.name, field.default)
            
        self.check_mandatory_fields()
    
    def check_mandatory_fields(self):
        for field in self.fields:
            if field.mandatory and getattr(self, field.name, None) is None:
                raise EntityMissingFieldError('Missing field %s in %s' % \
                                              (field.name, self.__class__.__name__))

# Subclasses of Entity are below; these represent the data in GTFS. 
# The attributes of each class are mapped in by create_and_map tables in
# map_entities.py:
# 
#  1. each Field in fields is mapped
#  2. cross-references are mapped in with the properties parameter of mapper()

class Agency(Entity):
    """A transit agency."""
    
    table_name = 'agency'
    gtfs_required = True
    
    # Note that agency_id is not mandatory according to GTFS. We assume here 
    # that agency_id and agency_name together are enough for a primary key - 
    # hope people aren't both omitting agency_ids and duping agency_names. 
    
    fields = [Field('agency_id', String, cast=str, primary_key=True),
              Field('agency_name', Unicode, cast=unicode, mandatory=True),
              Field('agency_url', String, cast=str, mandatory=True),
              Field('agency_timezone', PickleType, cast=pytz.timezone, mandatory=True),
              Field('agency_lang', String, cast=str),
              Field('agency_phone', String, cast=str),
              Field('agency_fare_url', String, cast=str),
             ]
    
    def __repr__(self):
        return '<Agency %s: %s>' % (getattr(self, 'agency_id', None), 
                                    self.agency_name)
    
    @property
    def routes_by_id(self):
        return dict(zip([x.route_id for x in self.routes], self.routes))

class Stop(Entity):
    """A physical stop, where passengers embark and disembark."""
    
    table_name = 'stops'
    gtfs_required = True
    
    fields = [Field('agency_id', String, cast=str, primary_key=True),
              Field('stop_id', String, cast=str, primary_key=True, mandatory=True),
              Field('stop_code', String, cast=str),
              Field('stop_name', Unicode, cast=unicode, mandatory=True),
              Field('stop_desc', Unicode, cast=unicode),
              Field('stop_lat', Float, cast=float, mandatory=True),
              Field('stop_lon', Float, cast=float, mandatory=True),
              Field('zone_id', String, cast=str),
              Field('stop_url', String, cast=str),
              Field('location_type', Integer, cast=int, default=0),
              Field('parent_station', String, cast=str),
              Field('stop_timezone', String, cast=pytz.timezone),
              Field('wheelchair_boarding', Integer, cast=int, default=0),
             ]

    def __repr__(self):
        return '<Stop %s: %s>' % (self.stop_id, self.stop_name)
    
    def __init__(self, **kwargs):
        Entity.__init__(self, **kwargs)
        if self.stop_lat < -180 or self.stop_lat > 180:
            raise EntityBadFieldError('stop_lat %f not in range [-180, 180] in %s' % \
                                      (self.stop_lat, repr(self)))
        if self.stop_lon < -180 or self.stop_lon > 180:
            raise EntityBadFieldError('stop_lon %f not in range [-180, 180] in %s' % \
                                      (self.stop_lon, repr(self)))
        if self.location_type not in [0,1]:
            raise EntityBadFieldError('location_type %d not in {0,1} in %s' % \
                                      (self.location_type, repr(self)))
        if self.wheelchair_boarding not in [0,1,2]:
            raise EntityBadFieldError('wheelchair_boarding %d not in {0,1,2} in %s' % \
                                      (self.wheelchair_boarding, repr(self)))

class Route(Entity):
    """A sequence of stops taken by a transit vehicle."""
    
    # Note: 16777215 = FFFFFF in hex
    
    table_name = 'routes'
    gtfs_required = True

    fields = [Field('agency_id', String, foreign_key='%s.agency_id' % Agency.table_name, cast=str, primary_key=True),
              Field('route_id', String, cast=str, primary_key=True, mandatory=True),
              Field('route_short_name', Unicode, cast=unicode, mandatory=True, default=''),
              Field('route_long_name', Unicode, cast=unicode, mandatory=True, default=''),
              Field('route_desc', Unicode, cast=unicode),
              Field('route_type', Integer, cast=int, mandatory=True),
              Field('route_url', String, cast=str),
              Field('route_color', Integer, cast=int_hex, default=16777215),
              Field('route_text_color', Integer, cast=int_hex, default=0),
             ]
    
    def __repr__(self):
        return '<Route %s: %s>' % (self.route_id, self.route_short_name)
    
    def __init__(self, **kwargs):
        Entity.__init__(self, **kwargs)
        if self.route_type not in range(8):
            raise EntityBadFieldError('route_type %d not an integer from 0 to 7 in %s' % \
                                      (self.route_type, repr(self)))
        if self.route_color < 0 or self.route_color > 16777215:
            raise EntityBadFieldError('route_color %s must be a hex between 000000 and FFFFFF in %s' % \
                                      (kwargs['route_color'], repr(self)))
        if self.route_color < 0 or self.route_text_color > 16777215:
            raise EntityBadFieldError('route_text_color %s must be a hex between 000000 and FFFFFF in %s' % \
                                      (kwargs['route_text_color'], repr(self)))
    
    @property
    def trips_by_id(self):
        return dict(zip([x.trip_id for x in self.trips], self.trips))

def bool_int(x):
    return bool(int(x))

class Service(Entity):
    """A calendar of service - indicates what days of week service is running."""
    
    table_name = 'calendar'
    gtfs_required = False   # if this is absent you must have a calendar_dates file
    
    fields = [Field('agency_id', String, cast=str, primary_key=True),
              Field('service_id', String, cast=str, primary_key=True, mandatory=True),
              Field('monday', Boolean, cast=bool_int, mandatory=True),
              Field('tuesday', Boolean, cast=bool_int, mandatory=True),
              Field('wednesday', Boolean, cast=bool_int, mandatory=True),
              Field('thursday', Boolean, cast=bool_int, mandatory=True),
              Field('friday', Boolean, cast=bool_int, mandatory=True),
              Field('saturday', Boolean, cast=bool_int, mandatory=True),
              Field('sunday', Boolean, cast=bool_int, mandatory=True),
              Field('start_date', Date, cast=date_yyyymmdd, mandatory=True),
              Field('end_date', Date, cast=date_yyyymmdd, mandatory=True),
             ]

    def __repr__(self):
        dayofweek = ''
        if self.monday: dayofweek += 'M'
        if self.tuesday: dayofweek += 'T'
        if self.wednesday: dayofweek += 'W'
        if self.thursday: dayofweek += 'Th'
        if self.friday: dayofweek += 'F'
        if self.saturday: dayofweek += 'S'
        if self.sunday: dayofweek += 'Su'
        return '<Service %s (%s)>' % (self.service_id, dayofweek)

    @property
    def trips_by_id(self):
        return dict(zip([x.trip_id for x in self.trips], self.trips))

class ServiceException(Entity):
    """Single-day exceptions to the rules in Services."""
    
    table_name = 'calendar_dates'
    gtfs_required = False
    
    fields = [Field('agency_id', String, cast=str, primary_key=True),
              Field('service_id', String, cast=str, primary_key=True, mandatory=True),
              Field('date', Date, cast=date_yyyymmdd, primary_key=True, mandatory=True),
              Field('exception_type', Integer, cast=int, mandatory=True),
             ]
    foreign_key_constraints = [ForeignKeyConstraint(['agency_id', 'service_id'], ['%s.agency_id' % Service.table_name, '%s.service_id' % Service.table_name])]

    def __repr__(self):
        return '<ServiceException %s: %s>' % (self.service_id, self.date)
    
    def __init__(self, **kwargs):
        Entity.__init__(self, **kwargs)
        if self.exception_type not in [1,2]:
            raise EntityBadFieldError('exception_type %d not 1 or 2 in %s' % \
                                      (self.exception_type, repr(self)))

class Trip(Entity):
    """A travel itinerary for a transit vehicle."""
    
    table_name = 'trips'
    gtfs_required = True

    fields = [Field('agency_id', String, cast=str, primary_key=True),
              Field('route_id', String, cast=str, mandatory=True),
              Field('service_id', String, cast=str, mandatory=True),
              Field('trip_id', String, cast=str, primary_key=True, mandatory=True),
              Field('trip_headsign', Unicode, cast=unicode),
              Field('trip_short_name', Unicode, cast=unicode),
              Field('direction_id', Integer, cast=int),
              Field('block_id', String, cast=str),
              Field('shape_id', String, cast=str),
             ]
    foreign_key_constraints = [ForeignKeyConstraint(['agency_id', 'route_id'], ['%s.agency_id' % Route.table_name, '%s.route_id' % Route.table_name]),
                               ForeignKeyConstraint(['agency_id', 'service_id'], ['%s.agency_id' % Service.table_name, '%s.service_id' % Service.table_name])]

    def __repr__(self):
        return '<Trip %s>' % self.trip_id
    
    def __init__(self, **kwargs):
        Entity.__init__(self, **kwargs)
        if getattr(self, 'direction_id', None) is not None:
            if self.direction_id not in [0,1]:
                raise EntityBadFieldError('direction_id %d not 1 or 2 in %s' % \
                                          (self.direction_id, repr(self)))

class StopTime(Entity):
    """A stop along a Trip: arrival and departure."""
    
    table_name = 'stop_times'
    gtfs_required = True
    
    fields = [Field('agency_id', String, cast=str, primary_key=True),
              Field('trip_id', String, cast=str, primary_key=True, mandatory=True),
              Field('arrival_time', Interval, cast=timedelta_hms, mandatory=True),
              Field('departure_time', Interval, cast=timedelta_hms, mandatory=True),
              Field('stop_id', String, cast=str, primary_key=True, mandatory=True),
              Field('stop_sequence', Integer, cast=int, primary_key=True, mandatory=True),
              Field('stop_headsign', Unicode, cast=unicode),
              Field('pickup_type', Integer, cast=int, default=0),
              Field('drop_off_type', Integer, cast=int, default=0),
              Field('shape_dist_traveled', Float, cast=float),
             ]
    foreign_key_constraints = [ForeignKeyConstraint(['agency_id', 'trip_id'], ['%s.agency_id' % Trip.table_name, '%s.trip_id' % Trip.table_name]),
                               ForeignKeyConstraint(['agency_id', 'stop_id'], ['%s.agency_id' % Stop.table_name, '%s.stop_id' % Stop.table_name])]

    def __repr__(self):
        return '<StopTime %s: %d>' % (self.trip_id, self.stop_sequence)
    
    def __init__(self, **kwargs):
        Entity.__init__(self, **kwargs)
        if self.arrival_time > self.departure_time:
            raise EntityBadFieldError('arrival time %s must be less than departure time %s in %s' % \
                                      (self.arrival_time, self.departure_time, repr(self)))
        if self.stop_sequence < 0:
            raise EntityBadFieldError('stop_sequence %d cannot be negative in %s' % \
                                      (self.stop_sequence, repr(self)))
        if self.pickup_type not in [0,1,2,3]:
            raise EntityBadFieldError('pickup_type %d not in {0,1,2,3} in %s' % \
                                      (self.pickup_type, repr(self)))
        if self.drop_off_type not in [0,1,2,3]:
              raise EntityBadFieldError('drop_off_type %d not in {0,1,2,3} in %s' % \
                                        (self.drop_off_type, repr(self)))

class Fare(Entity):
    """Passenger fare classifications."""
    
    table_name = 'fare_attributes'
    gtfs_required = False
    
    fields = [Field('agency_id', String, cast=str, primary_key=True),
              Field('fare_id', String, cast=str, primary_key=True, mandatory=True),
              Field('price', Float, cast=float, mandatory=True),
              Field('currency_type', String, cast=str, mandatory=True),
              Field('payment_method', Integer, cast=int, mandatory=True),
              Field('transfers', Integer, cast=int),
              Field('transfer_duration', Float, cast=float),
             ]

    def __repr__(self):
        return '<Fare %s>' % self.fare_id
    
    def __init__(self, **kwargs):
        Entity.__init__(self, **kwargs)
        if self.payment_method not in [0,1]:
            raise EntityBadFieldError('payment_method %d not in {0,1} in %s' % \
                                      (self.payment_method, repr(self)))

class FareRule(Entity):
    """Rules determining how fares are applied."""
    
    table_name = 'fare_rules'
    gtfs_required = False
    
    fields = [Field('agency_id', String, cast=str, primary_key=True),
              Field('fare_id', String, cast=str, primary_key=True, mandatory=True),
              Field('route_id', String, cast=str, primary_key=True, default=''),
              Field('origin_id', String, cast=str, primary_key=True, default=''),
              Field('destination_id', String, cast=str, primary_key=True, default=''),
              Field('contains_id', String, cast=str, primary_key=True, default=''),
             ]
    foreign_key_constraints = [ForeignKeyConstraint(['agency_id', 'fare_id'], ['%s.agency_id' % Fare.table_name, '%s.fare_id' % Fare.table_name]),
                               ForeignKeyConstraint(['agency_id', 'route_id'], ['%s.agency_id' % Route.table_name, '%s.route_id' % Route.table_name])]

    def __repr__(self):
        return '<FareRule %s: %s %s %s %s>' % (self.fare_id, 
                                               self.route_id,
                                               self.origin_id,
                                               self.destination_id,
                                               self.contains_id)

class ShapePoint(Entity):
    """Rules indicating how to draw lines on a map."""
    
    table_name = 'shapes'
    gtfs_required = False
    
    fields = [Field('agency_id', String, cast=str, primary_key=True),
              Field('shape_id', String, cast=str, primary_key=True, mandatory=True),
              Field('shape_pt_lat', Float, cast=float, primary_key=True, mandatory=True),
              Field('shape_pt_lon', Float, cast=float, primary_key=True, mandatory=True),
              Field('shape_pt_sequence', Integer, cast=int, primary_key=True, mandatory=True),
              Field('shape_dist_traveled', Float, cast=float),
             ]

    def __repr__(self):
        return '<ShapePoint %s>' % self.shape_id
    
    def __init__(self, **kwargs):
        Entity.__init__(self, **kwargs)
        if self.shape_pt_lat < -180 or self.shape_pt_lat > 180:
            raise EntityBadFieldError('shape_pt_lat %f not in [-180,180] in %s' % \
                                      (self.shape_pt_lat, repr(self)))
        if self.shape_pt_lon < -180 or self.shape_pt_lon > 180:
            raise EntityBadFieldError('shape_pt_lon %f not in [-180,180] in %s' % \
                                      (self.shape_pt_lon, repr(self)))
        if self.shape_pt_sequence < 0:
            raise EntityBadFieldError('shape_pt_sequence %d cannot be negative in %s' % \
                                      (self.shape_pt_sequence, repr(self)))

class Frequency(Entity):
    """Schedules without fixed stop times."""
    
    table_name = 'frequencies'
    gtfs_required = False
    
    fields = [Field('agency_id', String, cast=str, primary_key=True),
              Field('trip_id', String, cast=str, primary_key=True, mandatory=True),
              Field('start_time', Interval, cast=timedelta_hms, 
                    primary_key=True, mandatory=True),
              Field('end_time', Interval, cast=timedelta_hms, 
                    primary_key=True, mandatory=True),
              Field('headway_secs', Integer, cast=int, mandatory=True),
              Field('exact_times', Integer, cast=int, default=0)
             ]
    foreign_key_constraints = [ForeignKeyConstraint(['agency_id', 'trip_id'], ['%s.agency_id' % Trip.table_name, '%s.trip_id' % Trip.table_name])]

    def __repr__(self):
        return '<Frequency %s %s-%s>' % (self.trip_id, self.start_time, self.end_time)

    def __init__(self, **kwargs):
        Entity.__init__(self, **kwargs)
        if self.exact_times not in [0,1]:
            raise EntityBadFieldError('exact_times %d not in {0,1} in %s' % \
                                      (self.exact_times, repr(self)))

class Transfer(Entity):
    """Extra rules for transfers."""
    
    table_name = 'transfers'
    gtfs_required = False
    
    fields = [Field('agency_id', String, cast=str, primary_key=True),
              Field('from_stop_id', String,
                    cast=str, primary_key=True, mandatory=True),
              Field('to_stop_id', String,
                    cast=str, primary_key=True, mandatory=True),
              Field('transfer_type', Integer, cast=int, mandatory=True, default=0),
              Field('min_transfer_time', String, cast=str),
             ]
    foreign_key_constraints = [ForeignKeyConstraint(['agency_id', 'from_stop_id'], ['%s.agency_id' % Stop.table_name, '%s.stop_id' % Stop.table_name]),
                               ForeignKeyConstraint(['agency_id', 'to_stop_id'], ['%s.agency_id' % Stop.table_name, '%s.stop_id' % Stop.table_name])]

    def __repr__(self):
        return "<Transfer %s-%s>" % (self.from_stop_id, self.to_stop_id)

    def __init__(self, **kwargs):
        Entity.__init__(self, **kwargs)
        if self.transfer_type not in [0,1,2,3]:
            raise EntityBadFieldError('transfer_type %d not in {0,1,2,3} in %s' % \
                                      (self.transfer_type, repr(self)))

class FeedInfo(Entity):
    """Information about the feed."""
    
    table_name = 'feed_info'
    gtfs_required = False
    
    fields = [Field('agency_id', String, foreign_key='%s.agency_id' % Agency.table_name, cast=str, primary_key=True),
              Field('feed_publisher_name', Unicode, cast=unicode, primary_key=True, mandatory=True),
              Field('feed_publisher_url', String, cast=str, mandatory=True),
              Field('feed_lang', String, cast=str, mandatory=True),
              Field('feed_start_date', Date, cast=date_yyyymmdd),
              Field('feed_end_date', Date, cast=date_yyyymmdd),
              Field('feed_version', String, cast=str),
             ]
    
    def __repr__(self):
        return "<FeedInfo %s>" % self.feed_publisher_name