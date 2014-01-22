"""GTFS entities.

These are the entities returned by the various :py:mod:`pygtfs.schedule` lists.
Most of the attributes come directly from the gtfs reference. Also,
when possible relations are taken into account, e.g. a :py:class:`Route` class
has a `trips` attribute, with a list of trips for the specific route.
"""

from __future__ import division, absolute_import, print_function, unicode_literals


import datetime
import re

import pytz
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint
from sqlalchemy.types import Unicode, Integer, Float, Boolean, Date, Interval, PickleType, TypeDecorator, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates, synonym

Base = declarative_base()



def _validate_date(*field_names):
    @validates(*field_names)
    def make_date(self, key, value):
        return datetime.datetime.strptime(value, '%Y%m%d').date() 
    return make_date


def _validate_time_delta(*field_names):
    @validates(*field_names)
    def time_delta(self, key, value):
        (hours, minutes, seconds) = map(int, re.split(':', value))
        return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
    return time_delta
        

def _validate_int_bool(*field_names):
    @validates(*field_names)
    def int_bool(self, key, value):
        assert value in ["0","1"] , "value must be 0 or 1"
        return bool(int(value))
    return int_bool
            

def _validate_int_choice(int_choice, *field_names):
    @validates(*field_names)
    def in_range(self, key, value):
        if ((value is None) or (value == '')):
            if (None in int_choice):
                return None 
            else:
                raise ValueError("Empty value not allowed in {0}".format(key))
        else:
            int_value = int(value)
        assert int_value in int_choice, "value outside limits"
        return int_value
    return in_range

def _validate_float_range(float_min, float_max, *field_names):
    @validates(*field_names)
    def in_range(self, key, value):
        float_value = float(value)
        assert float_min <= float_value <= float_max, "value outside limits"
        return float_value
    return in_range

def create_foreign_keys(*key_names):
    """ Create foreign key constraints, always including feed_id,
        and relying on convention that key name is the same"""
    constraints = []
    for key in key_names:
        table, field = key.split('.')
        constraints.append(  ForeignKeyConstraint(["feed_id", field],[table+".feed_id", key]))
    return tuple(constraints)

class Feed(Base):
    __tablename__ = '_feed'
    _plural_name_ = 'feeds'
    feed_id = Column(Integer, primary_key=True)
    id = synonym('feed_id')
    feed_name = Column(Unicode)
    feed_append_date = Column(Date, nullable=True)


    # these relationships will allow us to delete entire feeds at once
    # by deleting a feed (because of 'cascading')

    agencies = relationship("Agency", backref=("feed"), cascade="all, delete-orphan")
    stops = relationship("Stop", backref=("feed"), cascade="all, delete-orphan")
    routes = relationship("Route", backref=("feed"), cascade="all, delete-orphan")
    trips = relationship("Trip", backref=("feed"), cascade="all, delete-orphan")
    stop_times = relationship("StopTime", backref=("feed"), cascade="all, delete-orphan")
    services = relationship("Service", backref=("feed"), cascade="all, delete-orphan")
    service_exceptions = relationship("ServiceException", backref=("feed"), cascade="all, delete-orphan")
    fares = relationship("Fare", backref=("feed"), cascade="all, delete-orphan")
    fare_rules = relationship("FareRule", backref=("feed"), cascade="all, delete-orphan")
    shape_points = relationship("ShapePoint", backref=("feed"), cascade="all, delete-orphan")
    frequencies = relationship("Frequency", backref=("feed"), cascade="all, delete-orphan")
    transfers = relationship("Transfer", backref=("feed"), cascade="all, delete-orphan")
    feedinfo = relationship("FeedInfo", backref=("feed"), cascade="all, delete-orphan")

    def __repr__(self):
        return '<Feed %s: %s>' % (self.feed_id, self.feed_name)

class Agency(Base):
    __tablename__ = 'agency'
    _plural_name_ = 'agencies'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    agency_id = Column(Unicode, primary_key=True, default=u"None")
    id = synonym('agency_id')
    agency_name = Column(Unicode)
    agency_url = Column(Unicode)
    agency_timezone = Column(Unicode)  #### pytz.timezone????
    agency_lang = Column(Unicode, nullable=True)
    agency_phone = Column(Unicode, nullable=True)
    agency_fare_url = Column(Unicode, nullable=True)

    routes = relationship("Route", backref="agency")

    def __repr__(self):
        return '<Agency %s: %s>' % (self.agency_id, self.agency_name)

class Stop(Base):
    __tablename__ = 'stops'
    _plural_name_ = 'stops'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    stop_id = Column(Unicode, primary_key=True)
    id = synonym('stop_id')
    stop_code = Column(Unicode, nullable=True)
    stop_name = Column(Unicode)
    stop_desc = Column(Unicode, nullable=True)
    stop_lat = Column(Float)
    stop_lon = Column(Float)
    zone_id = Column(Unicode, nullable=True)
    stop_url = Column(Unicode, nullable=True)
    location_type = Column(Integer, nullable=True)
    parent_station = Column(Integer, nullable=True)
    stop_timezone = Column(Unicode, nullable=True)
    wheelchair_boarding = Column(Integer, nullable=True)

    stop_times = relationship('StopTime', backref="stop")
    transfers_to = relationship('Transfer', backref="stop_to", foreign_keys='Transfer.to_stop_id')
    transfers_from = relationship('Transfer', backref="stop_from", foreign_keys='Transfer.from_stop_id')


    _validate_location = _validate_int_choice([0,1], 'location_type')
    _validate_wheelchair = _validate_int_choice([0,1,2], 'wheelchair_boarding')
    _validate_lon_lat = _validate_float_range(-180,180, 'stop_lon', 'stop_lat')

    def __repr__(self):
        return '<Stop %s: %s>' % (self.stop_id, self.stop_name)
            
class Route(Base):
    __tablename__ = 'routes'
    _plural_name_ = 'routes'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    route_id = Column(Unicode, primary_key=True)
    id = synonym('route_id')
    agency_id = Column(Unicode, default=u"None")
    route_short_name = Column(Unicode)
    route_long_name = Column(Unicode)
    route_desc = Column(Unicode, nullable=True)
    route_type = Column(Integer)
    route_url = Column(Unicode, nullable=True)
    route_color = Column(Unicode, nullable=True)
    route_text_color = Column(Unicode, nullable=True)

    __table_args__ = create_foreign_keys('agency.agency_id')

    trips = relationship("Trip", backref="route")
    fare_rules = relationship("FareRule", backref="route")
    
    _validate_route_type = _validate_int_choice(range(8), 'route_type')

    def __repr__(self):
        return '<Route %s: %s>' % (self.route_id, self.route_short_name)
    

class Trip(Base):
    __tablename__ = 'trips'
    _plural_name_ = 'trips'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    route_id = Column(Unicode)
    service_id = Column(Unicode)
    trip_id = Column(Unicode, primary_key=True)
    id = synonym('trip_id')
    trip_headsign = Column(Unicode, nullable=True)
    trip_short_name = Column(Unicode, nullable=True)
    direction_id = Column(Integer, nullable=True)
    block_id = Column(Unicode, nullable=True)
    shape_id = Column(Unicode, nullable=True)
    wheelchair_accessible = Column(Integer, nullable=True)

    stop_times = relationship("StopTime", backref="trip")
    frequencies = relationship("Frequency", backref="trip")

    __table_args__ = create_foreign_keys('routes.route_id', 'calendar.service_id', 'calendar_dates.service_id', 'shapes.shape_id')

    _validate_direction_id = _validate_int_choice([None,0,1], 'direction_id')
    _validate_wheelchair = _validate_int_choice([0,1,2], 'wheelchair_accessible')

    def __repr__(self):
        return '<Trip %s>' % self.trip_id

class StopTime(Base):
    __tablename__ = 'stop_times' 
    _plural_name_ = 'stop_times'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    trip_id = Column(Unicode, primary_key=True)
    arrival_time = Column(Interval)
    departure_time = Column(Interval)
    stop_id = Column(Unicode, primary_key=True)
    stop_sequence = Column(Integer, primary_key=True)
    stop_headsign = Column(Unicode)
    pickup_type = Column(Integer)
    drop_off_type = Column(Integer)
    shape_dist_traveled = Column(Integer)

    __table_args__ = create_foreign_keys('trips.trip_id', 'stops.stop_id')

    _validate_pickup_drop_off = _validate_int_choice([None,0,1,2,3], 'pickup_type', 'drop_off_type')
    _validate_arrival_departure = _validate_time_delta('arrival_time', 'departure_time')

    def __repr__(self):
        return '<StopTime %s: %d>' % (self.trip_id, self.stop_sequence)
    

class Service(Base):
    __tablename__ = 'calendar'
    _plural_name_ = 'services'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    service_id = Column(Unicode, primary_key=True)
    id = synonym('service_id')
    monday = Column(Boolean)
    tuesday = Column(Boolean)
    wednesday = Column(Boolean)
    thursday = Column(Boolean)
    friday = Column(Boolean)
    saturday = Column(Boolean)
    sunday = Column(Boolean)
    start_date = Column(Date)
    end_date = Column(Date)

    trips = relationship("Trip", backref="service")

    _validate_bools = _validate_int_bool('monday', 'tuesday', 'wednesday',
                                         'thursday', 'friday','saturday', 'sunday')
    _validate_dates = _validate_date('start_date', 'end_date')

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


class ServiceException(Base):
    __tablename__ = 'calendar_dates'
    _plural_name_ = 'service_excpetions'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    service_id = Column(Unicode, primary_key=True)
    id = synonym('service_id')
    date = Column(Date, primary_key=True)
    exception_type = Column(Integer)

    _validate_exception_type = _validate_int_choice([1,2], 'exception_type')
    _validate_dates = _validate_date('date')

    def __repr__(self):
        return '<ServiceException %s: %s>' % (self.service_id, self.date)


    

class Fare(Base):
    __tablename__ = 'fare_attributes'
    _plural_name_ = 'fares'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    fare_id = Column(Unicode, primary_key=True)
    id = synonym('fare_id')
    price = Column(Numeric)
    currency_type = Column(Unicode)
    payment_method = Column(Integer) 
    transfers = Column(Integer, nullable=True) # it is required, but allowed to be empty
    transfer_duration = Column(Integer, nullable=True)

    _validate_payment_method = _validate_int_choice([0,1], 'payment_method')
    _validate_transfers = _validate_int_choice([None, 0,1,2], 'transfers')

    def __repr__(self):
        return '<Fare %s>' % self.fare_id


class FareRule(Base):
    __tablename__ = 'fare_rules'
    _plural_name_ = 'fare_rules'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    fare_id = Column(Unicode, primary_key=True)
    route_id = Column(Unicode, nullable=True, primary_key=True)
    origin_id = Column(Unicode, ForeignKey('stops.zone_id'), nullable=True, primary_key=True)
    destination_id = Column(Unicode, ForeignKey('stops.zone_id'), nullable=True, primary_key=True)
    contains_id = Column(Unicode, ForeignKey('stops.zone_id'), nullable=True, primary_key=True)
    __table_args__ = create_foreign_keys('fare_attributes.fare_id', 'routes.route_id')

    def __repr__(self):
        return '<FareRule %s: %s %s %s %s>' % (self.fare_id,
                                               self.route_id,
                                               self.origin_id,
                                               self.destination_id,
                                               self.contains_id)


class ShapePoint(Base):
    __tablename__ = 'shapes'
    _plural_name_ = 'shapes'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    shape_id = Column(Unicode, primary_key=True)
    shape_pt_lat = Column(Float)
    shape_pt_lon = Column(Float)
    shape_pt_sequence = Column(Integer, primary_key=True)
    shape_dist_traveled = Column(Float)

    trips = relationship("Trip", backref="shape_points")

    _validate_lon_lat = _validate_float_range(-180,180, 'shape_pt_lon', 'shape_pt_lat')

    def __repr__(self):
        return '<ShapePoint %s>' % self.shape_id


class Frequency(Base):
    __tablename__ = 'frequencies'
    _plural_name_ = 'frequencies'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    trip_id = Column(Unicode, primary_key=True)
    start_time = Column(Interval, primary_key=True)
    end_time = Column(Interval, primary_key=True)
    headway_secs = Column(Integer)
    exact_times = Column(Integer, nullable=True)

    __table_args__ = create_foreign_keys('trips.trip_id')

    _validate_exact_times = _validate_int_choice([None,0,1], 'exact_times')
    _validate_deltas = _validate_time_delta('start_time', 'end_time')

    def __repr__(self):
        return '<Frequency %s %s-%s>' % (self.trip_id, self.start_time, self.end_time)

    
class Transfer(Base):
    __tablename__ = 'transfers'
    _plural_name_ = 'transfers'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    from_stop_id = Column(Unicode, ForeignKey('stops.stop_id'), primary_key=True)
    to_stop_id = Column(Unicode, ForeignKey('stops.stop_id'), primary_key=True)
    transfer_type = Column(Integer, nullable=True) # required but empty is allowed
    min_transfer_time = Column(Integer, nullable=True)

    _validate_transfer_type = _validate_int_choice([None,0,1,2,3], 'transfer_type')

    def __repr__(self):
        return "<Transfer %s-%s>" % (self.from_stop_id, self.to_stop_id)



class FeedInfo(Base):
    __tablename__ = 'feed_info'
    _plural_name_ = 'feed_infos'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    feed_publisher_name = Column(Unicode, primary_key=True)
    feed_publisher_url = Column(Unicode, primary_key=True)
    feed_lang = Column(Unicode)
    feed_start_date = Column(Date, nullable=True)
    feed_end_date = Column(Date, nullable=True)
    feed_version = Column(Unicode, nullable=True)

    _validate_start_end = _validate_date('feed_start_date', 'feed_end_date')

    def __repr__(self):
        return "<FeedInfo %s>" % self.feed_publisher_name
     

# a feed can skip Service (calendar) if it has ServiceException (calendar_dates)

gtfs_required = [Agency, Stop, Route, Trip, StopTime]
gtfs_calendar = [Service, ServiceException]
gtfs_not_required = [Fare, FareRule, ShapePoint, Frequency, Transfer, FeedInfo]
gtfs_all = gtfs_required + gtfs_calendar + gtfs_not_required
