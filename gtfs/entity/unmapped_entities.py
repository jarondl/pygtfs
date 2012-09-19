
from sqlalchemy import Column, ForeignKey, String, Integer, Float, Boolean, Time, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Agency(Base):
    
    __tablename__ = 'agency'
    isGTFSRequired = True
    
    agency_id = Column(String, primary_key=True)
    agency_name = Column(String)
    agency_url = Column(String)
    agency_timezone = Column(String)
    agency_lang = Column(String)
    agency_phone = Column(String)
    agency_fare_url = Column(String)
    
    def __repr__(self):
        return '<Agency %s>' % self.agency_id

class Stop(Base):
    
    __tablename__ = 'stops'
    isGTFSRequired = True
    
    stop_id = Column(String, primary_key=True)
    stop_code = Column(String)
    stop_name = Column(String)
    stop_desc = Column(String)
    stop_lat = Column(Float)
    stop_lon = Column(Float)
    zone_id = Column(String)
    stop_url = Column(String)
    location_type = Column(String)
    parent_station = Column(String)

    def __repr__(self):
        return '<Stop %s>' % self.stop_id

class Route(Base):
    
    __tablename__ = 'routes'
    isGTFSRequired = True

    route_id = Column(String, primary_key=True)
    agency_id = Column(String, ForeignKey('%s.agency_id' % Agency.__tablename__))
    route_short_name = Column(String)
    route_long_name = Column(String)
    route_desc = Column(String)
    route_type = Column(Integer)
    route_url = Column(String)
    route_color = Column(String)
    route_text_color = Column(String)
    
    def __repr__(self):
        return '<Route %s>' % self.route_id

# Note: using calendar_dates.txt without calendar.txt is not yet supported

class Service(Base):
    
    __tablename__ = 'calendar'
    isGTFSRequired = True
    
    service_id = Column(String, primary_key=True)
    monday = Column(Boolean)
    tuesday = Column(Boolean)
    wednesday = Column(Boolean)
    thursday = Column(Boolean)
    friday = Column(Boolean)
    saturday = Column(Boolean)
    sunday = Column(Boolean)
    start_date = Column(Date)
    end_date = Column(Date)

    def __repr__(self):
        return '<Service %s>' % self.service_id

class ServiceException(Base):
    
    __tablename__ = 'calendar_dates'
    isGTFSRequired = False
    
    service_id = Column(String, ForeignKey('%s.service_id' % Service.__tablename__), 
                        primary_key=True)
    date = Column(Date, primary_key=True)
    exception_type = Column(String)

    def __repr__(self):
        return '<ServiceException %s %s>' % (self.service_id, self.date)

class Trip(Base):
    
    __tablename__ = 'trips'
    isGTFSRequired = True
    
    route_id = Column(String, ForeignKey('%s.route_id' % Route.__tablename__))
    service_id = Column(String, ForeignKey('%s.service_id' % Service.__tablename__))
    trip_id = Column(String, primary_key=True)
    trip_headsign = Column(String)
    trip_short_name = Column(String)
    direction_id = Column(String)
    block_id = Column(String)
    shape_id = Column(String)

    def __repr__(self):
        return '<Trip %s>' % self.trip_id

class StopTime(Base):
    
    __tablename__ = 'stop_times'
    isGTFSRequired = True
    
    trip_id = Column(String, ForeignKey('%s.trip_id' % Trip.__tablename__), 
                     primary_key=True)
    arrival_time = Column(Time)
    departure_time = Column(Time)
    stop_id = Column(String, ForeignKey('%s.stop_id' % Stop.__tablename__), 
                     primary_key=True)
    stop_sequence = Column(Integer, primary_key=True)
    stop_headsign = Column(String)
    pickup_type = Column(String)
    drop_off_type = Column(String)
    shape_dist_traveled = Column(Float)

    def __repr__(self):
        return '<StopTime %s-%s %d>' % (self.trip_id, 
                                        self.stop_id, 
                                        self.stop_sequence)
                                        
class Fare(Base):
    
    __tablename__ = 'fare_attributes'
    isGTFSRequired = False
    
    fare_id = Column(String, primary_key=True)
    price = Column(String)
    currency_type = Column(String)
    payment_method = Column(String)
    transfers = Column(Integer)
    transfer_duration = Column(String)

    def __repr__(self):
        return '<Fare %s>' % (self.fare_id)

class FareRule(Base):
    
    __tablename__ = 'fare_rules'
    isGTFSRequired = False
    
    fare_id = Column(String, ForeignKey('%s.fare_id', Fare.__tablename__), 
                     primary_key=True)
    route_id = Column(String, ForeignKey('%s.route_id', Route.__tablename__), 
                      primary_key=True)
    origin_id = Column(String, primary_key=True)
    destination_id = Column(String, primary_key=True)
    contains_id = Column(String, primary_key=True)
    
    def __repr__(self):
        return '<FareRule %s: %s %s %s %s>' % (self.fare_id, 
                                               self.route_id,
                                               self.origin_id,
                                               self.destination_id,
                                               self.contains_id)

class ShapePoint(Base):
    
    __tablename__ = 'shapes'
    isGTFSRequired = False
    
    shape_id = Column(String, primary_key=True)
    shape_pt_lat = Column(String)
    shape_pt_lon = Column(String)
    shape_pt_sequence = Column(Integer)
    shape_dist_traveled = Column(String)

    def __repr__(self):
        return '<ShapePoint %s>' % self.shape_id

class Frequency(Base):
    
    __tablename__ = 'frequencies'
    isGTFSRequired = False
    
    trip_id = Column(String, ForeignKey('%s.trip_id' % Trip.__tablename__), 
                     primary_key=True)
    start_time = Column(String, primary_key=True)
    end_time = Column(String, primary_key=True)
    headway_secs = Column(Integer)

    def __repr__(self):
        return '<Frequency %s %s-%s>' % (self.trip_id,
                                         self.start_time,
                                         self.end_time)

class Transfer(Base):
    
    __tablename__ = 'transfers'
    isGTFSRequired = False
    
    from_stop_id = Column(String, ForeignKey('%s.stop_id' % Stop.__tablename__), 
                          primary_key=True)
    to_stop_id = Column(String, ForeignKey('%s.stop_id' % Stop.__tablename__),
                        primary_key=True)
    transfer_type = Column(Integer)
    min_transfer_time = Column(String)

    def __repr__(self):
        return "<Transfer %s-%s>" % (self.from_stop_id, self.to_stop_id)