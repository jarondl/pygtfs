"""GTFS entities.

These are the entities returned by the various :py:mod:`pygtfs.schedule` lists.
Most of the attributes come directly from the gtfs reference. Also,
when possible relations are taken into account, e.g. a :py:class:`Route` class
has a `trips` attribute, with a list of trips for the specific route.
"""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)

import datetime

from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, and_, Table, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates, synonym, foreign
from sqlalchemy.types import (Unicode, Integer, Float, Boolean, Date, Interval,
                              Numeric)

from .exceptions import PygtfsValidationError

Base = declarative_base()


def _validate_date(*field_names):
    @validates(*field_names)
    def make_date(self, key, value):
        return datetime.datetime.strptime(value, '%Y%m%d').date()
    return make_date


def _validate_time_delta(*field_names):
    @validates(*field_names)
    def time_delta(self, key, value):
        if value is None or value == "":
            return None
        (hours, minutes, seconds) = map(int, value.split(":"))
        return datetime.timedelta(hours=hours, minutes=minutes,
                                  seconds=seconds)
    return time_delta


def _validate_int_bool(*field_names):
    @validates(*field_names)
    def int_bool(self, key, value):
        if value not in ("0", "1"):
            raise PygtfsValidationError("{0} must be 0 or 1, "
                                        "was {1}".format(key, value))
        return value == "1"
    return int_bool


def _validate_int_choice(int_choice, *field_names):
    @validates(*field_names)
    def in_range(self, key, value):
        if value is None or value == "":
            if (None in int_choice):
                return None
            else:
                raise PygtfsValidationError("Empty value not allowed in {0}".format(key))
        else:
            int_value = int(value)
        if int_value not in int_choice:
            raise PygtfsValidationError(
                "{0} must be in range {1}, was {2}".format(key, int_choice, value))
        return int_value
    return in_range


def _validate_float_range(float_min, float_max, *field_names):
    @validates(*field_names)
    def in_range(self, key, value):
        float_value = float(value)
        if not (float_min <= float_value <= float_max):
            raise PygtfsValidationError(
                "{0} must be in range [{1}, {2}],"
                " was {2}".format(key, float_min, float_max, value))
        return float_value
    return in_range


def _validate_float_none(*field_names):
    @validates(*field_names)
    def is_float_none(self, key, value):
        try:
            return float(value)
        except ValueError:
            if value is None or value == "":
                return None
            else:
                raise
    return is_float_none


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
    translations = relationship("Translation", backref=("feed"), cascade="all, delete-orphan")

    def __repr__(self):
        return '<Feed %s: %s>' % (self.feed_id, self.feed_name)


class Agency(Base):
    __tablename__ = 'agency'
    _plural_name_ = 'agencies'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    agency_id = Column(Unicode, primary_key=True, default="None", index=True)
    id = synonym('agency_id')
    agency_name = Column(Unicode)
    agency_url = Column(Unicode)
    agency_timezone = Column(Unicode)  # ### pytz.timezone????
    agency_lang = Column(Unicode, nullable=True)
    agency_phone = Column(Unicode, nullable=True)
    agency_fare_url = Column(Unicode, nullable=True)
    agency_email = Column(Unicode, nullable=True)

    def __repr__(self):
        return '<Agency %s: %s>' % (self.agency_id, self.agency_name)


class Stop(Base):
    __tablename__ = 'stops'
    _plural_name_ = 'stops'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    stop_id = Column(Unicode, primary_key=True, index=True)
    id = synonym('stop_id')
    stop_code = Column(Unicode, nullable=True, index=True)
    stop_name = Column(Unicode)
    stop_desc = Column(Unicode, nullable=True)
    stop_lat = Column(Float)
    stop_lon = Column(Float)
    zone_id = Column(Unicode, nullable=True)
    stop_url = Column(Unicode, nullable=True)
    location_type = Column(Integer, nullable=True)
    parent_station = Column(Unicode, nullable=True)
    stop_timezone = Column(Unicode, nullable=True)
    wheelchair_boarding = Column(Integer, nullable=True)
    platform_code = Column(Unicode, nullable=True)

    translations = relationship('Translation', secondary='_stop_translations')

    __table_args__ = (Index('idx_stop_for_translations', feed_id, stop_name, stop_id),)

    _validate_location = _validate_int_choice([None, 0, 1, 2, 3, 4], 'location_type')
    _validate_wheelchair = _validate_int_choice([None, 0, 1, 2],
                                                'wheelchair_boarding')
    _validate_lon_lat = _validate_float_range(-180, 180, 'stop_lon',
                                              'stop_lat')

    def __repr__(self):
        return '<Stop %s: %s>' % (self.stop_id, self.stop_name)


class Route(Base):
    __tablename__ = 'routes'
    _plural_name_ = 'routes'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    route_id = Column(Unicode, primary_key=True, index=True)
    id = synonym('route_id')
    agency_id = Column(Unicode, default="None")
    route_short_name = Column(Unicode)
    route_long_name = Column(Unicode)
    route_desc = Column(Unicode, nullable=True)
    route_type = Column(Integer)
    route_url = Column(Unicode, nullable=True)
    route_color = Column(Unicode, nullable=True)
    route_text_color = Column(Unicode, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint([feed_id, agency_id], [Agency.feed_id, Agency.agency_id]),
    )

    agency = relationship(Agency, backref="routes",
            primaryjoin=and_(Agency.agency_id==foreign(agency_id),
                             Agency.feed_id==feed_id))

    # https://developers.google.com/transit/gtfs/reference/extended-route-types
    valid_extended_route_types = [
        range(8),
        range(11, 13),
        range(100, 118),
        range(200, 210),
        [300],
        range(400, 406),
        [500],
        [600],
        range(700, 717),
        [800],
        range(900, 907),
        range(1000, 1022),
        range(1100, 1115),
        [1200],
        range(1300, 1308),
        range(1400, 1403),
        range(1500, 1508),
        range(1600, 1605),
        range(1700, 1703)
    ]
    # flatten the list of lists to a list
    valid_extended_route_types = [item for sublist in valid_extended_route_types for item in sublist]
    _validate_route_type = _validate_int_choice(valid_extended_route_types, 'route_type')

    def __repr__(self):
        return '<Route %s: %s>' % (self.route_id, self.route_short_name)


class ShapePoint(Base):
    __tablename__ = 'shapes'
    _plural_name_ = 'shapes'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    shape_id = Column(Unicode, primary_key=True)
    shape_pt_lat = Column(Float)
    shape_pt_lon = Column(Float)
    shape_pt_sequence = Column(Integer, primary_key=True)
    shape_dist_traveled = Column(Float, nullable=True)

    __table_args__ = (
        Index('idx_shape_for_trips', feed_id, shape_id),
    )

    _validate_lon_lat = _validate_float_range(-180, 180,
                                              'shape_pt_lon', 'shape_pt_lat')
    _validate_shape_dist_traveled = _validate_float_none('shape_dist_traveled')

    def __repr__(self):
        return '<ShapePoint %s>' % self.shape_id


class Service(Base):
    __tablename__ = 'calendar'
    _plural_name_ = 'services'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    service_id = Column(Unicode, primary_key=True, index=True)
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

    _validate_bools = _validate_int_bool('monday', 'tuesday', 'wednesday',
                                         'thursday', 'friday', 'saturday',
                                         'sunday')
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
    _plural_name_ = 'service_exceptions'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    service_id = Column(Unicode, primary_key=True, index=True)
    id = synonym('service_id')
    date = Column(Date, primary_key=True)
    exception_type = Column(Integer)

    _validate_exception_type = _validate_int_choice([1, 2], 'exception_type')
    _validate_dates = _validate_date('date')

    def __repr__(self):
        return '<ServiceException %s: %s>' % (self.service_id, self.date)


class Trip(Base):
    __tablename__ = 'trips'
    _plural_name_ = 'trips'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    route_id = Column(Unicode)
    service_id = Column(Unicode)
    trip_id = Column(Unicode, primary_key=True, index=True)
    id = synonym('trip_id')
    trip_headsign = Column(Unicode, nullable=True)
    trip_short_name = Column(Unicode, nullable=True)
    direction_id = Column(Integer, nullable=True)
    block_id = Column(Unicode, nullable=True)
    shape_id = Column(Unicode, nullable=True)
    wheelchair_accessible = Column(Integer, nullable=True)
    bikes_allowed = Column(Integer, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint([feed_id, route_id], [Route.feed_id, Route.route_id]),
        ForeignKeyConstraint([feed_id, service_id], [Service.feed_id, Service.service_id]),
        Index('idx_trips_shape_id', feed_id, shape_id),
    )

    route = relationship(Route, backref="trips",
            primaryjoin=and_(Route.route_id==foreign(route_id),
                             Route.feed_id==feed_id))

    shape_points = relationship(ShapePoint, backref="trips",
            secondary="_trip_shapes")

    # TODO: The service_id references to calendar or to calendar_dates.
    # Need to implement this requirement, but not using a simple foreign key.
    service = relationship(Service, backref='trips',
              primaryjoin=and_(foreign(service_id) == Service.service_id,
                               feed_id == Service.feed_id))


    _validate_direction_id = _validate_int_choice([None, 0, 1], 'direction_id')
    _validate_wheelchair = _validate_int_choice([None, 0, 1, 2],
                                                'wheelchair_accessible')
    _validate_bikes = _validate_int_choice([None, 0, 1, 2], 'bikes_allowed')

    def __repr__(self):
        return '<Trip %s>' % self.trip_id


class Translation(Base):
    __tablename__ = 'translations'
    _plural_name_ = 'translations'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    trans_id = Column(Unicode, primary_key=True, index=True)
    lang = Column(Unicode, primary_key=True)
    translation = Column(Unicode)

    __table_args__ = (Index('idx_translations_for_stops', feed_id, trans_id),)

    def __repr__(self):
        return '<Translation %s (to %s): %s>' % (self.trans_id, self.lang,
                                                 self.translation)


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
    shape_dist_traveled = Column(Numeric, nullable=True)
    timepoint = Column(Integer, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint([feed_id, stop_id], [Stop.feed_id, Stop.stop_id]),
        ForeignKeyConstraint([feed_id, trip_id], [Trip.feed_id, Trip.trip_id]),
    )

    stop = relationship(Stop, backref='stop_times',
            primaryjoin=and_(Stop.stop_id==foreign(stop_id),
                             Stop.feed_id==feed_id))
    trip = relationship(Trip, backref="stop_times",
            primaryjoin=and_(Trip.trip_id==foreign(trip_id),
                             Trip.feed_id==feed_id))

    _validate_pickup_drop_off = _validate_int_choice([None, 0, 1, 2, 3],
                                                     'pickup_type',
                                                     'drop_off_type')
    _validate_arrival_departure = _validate_time_delta('arrival_time',
                                                       'departure_time')
    _validate_timepoint = _validate_int_choice([None, 0, 1], 'timepoint')

    def __repr__(self):
        return '<StopTime %s: %d>' % (self.trip_id, self.stop_sequence)


class Fare(Base):
    __tablename__ = 'fare_attributes'
    _plural_name_ = 'fares'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    fare_id = Column(Unicode, primary_key=True, index=True)
    id = synonym('fare_id')
    price = Column(Numeric)
    currency_type = Column(Unicode)
    payment_method = Column(Integer)
    transfers = Column(Integer, nullable=True)  # required, empty is allowed
    transfer_duration = Column(Integer, nullable=True)
    agency_id = Column(Unicode, nullable=True)

    _validate_payment_method = _validate_int_choice([0, 1], 'payment_method')
    _validate_transfers = _validate_int_choice([None, 0, 1, 2, 3, 4, 5], 'transfers')

    def __repr__(self):
        return '<Fare %s>' % self.fare_id


class FareRule(Base):
    __tablename__ = 'fare_rules'
    _plural_name_ = 'fare_rules'
    fare_rule_internal_key = Column(Integer, primary_key=True)
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'))
    fare_id = Column(Unicode)
    # TODO: Add uniqueness constraints for fare_id,route_id,and the three
    # zone_ids.
    route_id = Column(Unicode, nullable=True)

    # TODO: add a constraint such that, each one of the following attributes
    # must be one of the `stops.zone_id`s
    origin_id = Column(Unicode, nullable=True)
    destination_id = Column(Unicode, nullable=True)
    contains_id = Column(Unicode, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint([feed_id, route_id], [Route.feed_id, Route.route_id]),
    )

    route = relationship(Route, backref="fare_rules",
            primaryjoin=and_(Route.route_id==foreign(route_id),
                             Route.feed_id==feed_id))

    def __repr__(self):
        return '<FareRule %s: %s %s %s %s>' % (self.fare_id,
                                               self.route_id,
                                               self.origin_id,
                                               self.destination_id,
                                               self.contains_id)


class Frequency(Base):
    __tablename__ = 'frequencies'
    _plural_name_ = 'frequencies'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    trip_id = Column(Unicode, primary_key=True)
    start_time = Column(Interval, primary_key=True)
    end_time = Column(Interval, primary_key=True)
    headway_secs = Column(Integer)
    exact_times = Column(Integer, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint([feed_id, trip_id], [Trip.feed_id, Trip.trip_id]),
    )

    trip = relationship(Trip, backref="frequencies",
            primaryjoin=and_(Trip.trip_id==foreign(trip_id),
                             Trip.feed_id==feed_id))

    _validate_exact_times = _validate_int_choice([None, 0, 1], 'exact_times')
    _validate_deltas = _validate_time_delta('start_time', 'end_time')

    def __repr__(self):
        return '<Frequency %s %s-%s>' % (self.trip_id, self.start_time,
                                         self.end_time)


class Transfer(Base):
    __tablename__ = 'transfers'
    _plural_name_ = 'transfers'
    feed_id = Column(Integer, ForeignKey('_feed.feed_id'), primary_key=True)
    from_stop_id = Column(Unicode, primary_key=True)
    to_stop_id = Column(Unicode, primary_key=True)
    # Not null with default empty string to keep PostgreSQL happy
    from_route_id = Column(Unicode, primary_key=True, nullable=False, default="")
    to_route_id = Column(Unicode, primary_key=True, nullable=False, default="")
    from_trip_id = Column(Unicode, primary_key=True, nullable=False, default="")
    to_trip_id = Column(Unicode, primary_key=True, nullable=False, default="")
    transfer_type = Column(Integer, nullable=True)  # required; allowed empty
    min_transfer_time = Column(Integer, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint([feed_id, from_stop_id], [Stop.feed_id, Stop.stop_id]),
        ForeignKeyConstraint([feed_id, to_stop_id], [Stop.feed_id, Stop.stop_id]),
    )

    stop_to = relationship(Stop, backref="transfers_to",
                           primaryjoin=and_(Stop.stop_id == foreign(to_stop_id),
                                            Stop.feed_id == feed_id))
    stop_from = relationship(Stop, backref="transfers_from",
                             primaryjoin=and_(Stop.stop_id == foreign(from_stop_id),
                                              Stop.feed_id == feed_id))
    route_from = relationship(Route, backref="transfers_from",
                              primaryjoin=and_(Route.route_id == foreign(from_route_id),
                                               Route.feed_id == feed_id))
    route_to = relationship(Route, backref="transfers_to",
                            primaryjoin=and_(Route.route_id == foreign(to_route_id),
                                             Route.feed_id == feed_id))
    trip_from = relationship(Trip, backref="transfers_from",
                             primaryjoin=and_(Trip.trip_id == foreign(from_trip_id),
                                              Trip.feed_id == feed_id))
    trip_to = relationship(Trip, backref="transfers_to",
                           primaryjoin=and_(Trip.trip_id == foreign(to_trip_id),
                                            Trip.feed_id == feed_id))

    _validate_transfer_type = _validate_int_choice([None, 0, 1, 2, 3],
                                                   'transfer_type')

    def __repr__(self):
        return "<Transfer from (%s, %s, %s) to (%s, %s, %s)>" % (self.from_stop_id, self.from_route_id,
                                                                 self.from_trip_id, self.to_stop_id,
                                                                 self.to_route_id, self.to_trip_id)


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


# Many-to-many secondary tables. Make sure to also load them properly in
# loader.py
_stop_translations = Table(
    '_stop_translations', Base.metadata,
    Column('stop_feed_id', Integer),
    Column('translation_feed_id', Integer),
    Column('stop_id', Unicode),
    Column('trans_id', Unicode),
    Column('lang', Unicode),
    ForeignKeyConstraint(['stop_feed_id', 'stop_id'], [Stop.feed_id, Stop.stop_id]),
    ForeignKeyConstraint(['translation_feed_id', 'trans_id', 'lang'], [Translation.feed_id, Translation.trans_id, Translation.lang]),
)


_trip_shapes = Table(
    '_trip_shapes', Base.metadata,
    Column('trip_feed_id', Integer),
    Column('shape_feed_id', Integer),
    Column('trip_id', Unicode),
    Column('shape_id', Unicode),
    Column('shape_pt_sequence', Integer),
    ForeignKeyConstraint(['trip_feed_id', 'trip_id'], [Trip.feed_id, Trip.trip_id]),
    ForeignKeyConstraint(['shape_feed_id', 'shape_id', 'shape_pt_sequence'],
        [ShapePoint.feed_id, ShapePoint.shape_id, ShapePoint.shape_pt_sequence]),
)


# a feed can skip Service (calendar) if it has ServiceException(calendar_dates)
gtfs_required = {Agency, Stop, Route, Trip, StopTime}
gtfs_calendar = {Service, ServiceException}
# gtfs all must maintain the right insertion order due to dependencies.
gtfs_all = [Agency, Stop, Transfer, Route, Fare, FareRule, ShapePoint,
            Service, ServiceException, Trip, Frequency, StopTime, FeedInfo,
            Translation]
