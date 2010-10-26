from ..types import make_gtfs_foreign_key_class, Boolean, Time, Date

class Entity(object):
  def __init__(self, **kwargs):
    for attrname, attrtype in self.FIELDS:
      if attrname in kwargs:
        attrvaluestr = kwargs[attrname]
	if attrvaluestr == '':
	  attrvalue = None
	else:
	  attrvalue = attrtype( attrvaluestr )

        setattr( self, attrname, attrvalue )

class ShapePoint(Entity):
  TABLENAME = "shapes"
  FIELDS = (('shape_id',str),
            ('shape_pt_lat',str),
	    ('shape_pt_lon',str),
	    ('shape_pt_sequence',int),
	    ('shape_dist_traveled',str))
  ID_FIELD = None

  def __repr__(self):
    return "<ShapePoint #%s (%s, %s)>"%(self.shape_pt_sequence,self.shape_pt_lat,self.shape_pt_lon)

class Agency(Entity):
  TABLENAME = "agency"
  FIELDS = (('agency_id',str),
            ('agency_name',str),
	    ('agency_url',str),
	    ('agency_timezone',str),
	    ('agency_lang',str),
	    ('agency_phone',str))
  ID_FIELD = "agency_id"

  def __repr__(self):
    return "<Agency %s>"%self.agency_id

  def __init__(self,**kwargs):
    Entity.__init__(self, **kwargs)

    if not hasattr( self, "agency_id" ) or self.agency_id is None:
      self.agency_id = "__DEFAULT__"

class ServicePeriod(Entity):
  TABLENAME = "calendar"
  FIELDS = (('service_id', str),
            ('monday', Boolean),
	    ('tuesday', Boolean),
	    ('wednesday', Boolean),
	    ('thursday', Boolean),
	    ('friday', Boolean),
	    ('saturday', Boolean),
	    ('sunday', Boolean),
	    ('start_date', Date),
	    ('end_date', Date))
  ID_FIELD = "service_id"

  def __repr__(self):
    return "<ServicePeriod %s %s%s%s%s%s%s%s>"%(self.service_id,
                                           self.monday,
					   self.tuesday,
					   self.wednesday,
					   self.thursday,
					   self.friday,
					   self.saturday,
					   self.sunday)

class ServiceException(Entity):
  TABLENAME = "calendar_dates"
  FIELDS = (('service_id', make_gtfs_foreign_key_class(ServicePeriod)),
            ('date', Date),
	    ('exception_type', str))
  ID_FIELD = None

  def __repr__(self):
    return "<ServiceException %s %s>"%(self.date, self.exception_type)

class Route(Entity):
  TABLENAME = "routes"
  FIELDS = (('route_id',str),
            ('agency_id',make_gtfs_foreign_key_class(Agency)),
	    ('route_short_name',str),
	    ('route_long_name',str),
	    ('route_desc',str),
	    ('route_type',int),
	    ('route_url',str),
	    ('route_color',str),
	    ('route_text_color',str))
  ID_FIELD = "route_id"

  def __repr__(self):
    return "<Route %s>"%self.route_id

  def __init__(self, **kwargs):
    Entity.__init__(self, **kwargs)

    if not hasattr( self, "agency_id" ) or self.agency_id is None:
      self.agency_id = "__DEFAULT__"

class Stop(Entity):
  TABLENAME = "stops"
  FIELDS = (('stop_id',str),
            ('stop_code',str),
	    ('stop_name',str),
	    ('stop_desc',str),
	    ('stop_lat',float),
	    ('stop_lon',float),
	    ('zone_id',str),
	    ('stop_url',str),
	    ('location_type',str),
	    ('parent_station',str))
  ID_FIELD = "stop_id"

  def __repr__(self):
    return "<Stop %s>"%self.stop_id

class Trip(Entity):
  TABLENAME = "trips"
  FIELDS = (('route_id',make_gtfs_foreign_key_class(Route)),
            ('service_id',make_gtfs_foreign_key_class(ServicePeriod)),
	    ('trip_id',str),
	    ('trip_headsign',str),
	    ('trip_short_name',str),
	    ('direction_id',str),
	    ('block_id',str),
	    ('shape_id',str))
  ID_FIELD = "trip_id"

  def __repr__(self):
    return "<Trip %s>"%self.trip_id

class StopTime(Entity):
  TABLENAME = "stop_times"
  FIELDS = (('trip_id',make_gtfs_foreign_key_class(Trip)),
            ('arrival_time',Time),
	    ('departure_time',Time),
	    ('stop_id',make_gtfs_foreign_key_class(Stop)),
	    ('stop_sequence',int),
	    ('stop_headsign',str),
	    ('pickup_type',str),
	    ('drop_off_type',str),
	    ('shape_dist_traveled',float))
  ID_FIELD = None
  
  def __repr__(self):
    return "<StopTime %s %s>"%(self.trip_id,self.departure_time)

class Fare(Entity):
  TABLENAME = "fare_attributes"
  FIELDS = (('fare_id',str),
            ('price',str),
	    ('currency_type',str),
	    ('payment_method',str),
	    ('transfers',int),
	    ('transfer_duration',str))
  ID_FIELD = 'fare_id'

  def __repr__(self):
    return "<Fare %s %s>"%(self.price,self.currency_type)

class FareRule(Entity):
  TABLENAME = "fare_rules"
  FIELDS = (('fare_id',make_gtfs_foreign_key_class(Fare)),
            ('route_id',make_gtfs_foreign_key_class(Route)),
	    ('origin_id',str),
	    ('destination_id',str),
	    ('contains_id',str))
  ID_FIELD = None

class Frequency(Entity):
  TABLENAME = "frequencies"
  FIELDS = (('trip_id',make_gtfs_foreign_key_class(Trip)),
            ('start_time',str),
	    ('end_time',str),
	    ('headway_secs',int))
  ID_FIELD = None

  def __repr__(self):
    return "<Frequency %s-%s %s>"%(self.start_time,self.end_time,self.headway_secs)

class Transfer(Entity):
  TABLENAME = "transfers"
  FIELDS = (('from_stop_id',make_gtfs_foreign_key_class(Stop)),
            ('to_stop_id',make_gtfs_foreign_key_class(Stop)),
	    ('transfer_type',int),
	    ('min_transfer_time',str))
  ID_FIELD = None
