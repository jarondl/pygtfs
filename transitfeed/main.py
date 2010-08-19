import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
import os
from codecs import iterdecode
from zipfile import ZipFile
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql.expression import ColumnElement

class GTFSForeignKey(str):
  pass

def make_gtfs_foreign_key_class(cls):
  class ret(GTFSForeignKey):
    _cls = cls
  return ret

class GTFSField(object):
  def __init__(self, fieldtype):
    self.fieldtype = fieldtype

class GTFSEntity(object):
  def __init__(self):
    pass

  @classmethod
  def fields(cls):
    print cls.__dict__

    for name,attr in cls.__dict__.items():
      if isinstance( attr, GTFSField ):
        yield( name, attr )

  def __init__(self, **kwargs):
    for attrname, attrtype in self.FIELDS:
      if attrname in kwargs:
        attrvaluestr = kwargs[attrname]
	if attrvaluestr == '':
	  attrvalue = None
	else:
	  attrvalue = attrtype( attrvaluestr )

        setattr( self, attrname, attrvalue )


def table_def_from_entity(entity_class, metadata):
  sqlalchemy_types = {str:String,int:Integer}
  columns = []
  for field_name,field_type in entity_class.FIELDS:
    if issubclass(field_type, GTFSForeignKey):
      foreign_key_column_name = field_type._cls.TABLENAME+"."+field_type._cls.ID_FIELD
      columns.append( Column( field_name, String, ForeignKey(foreign_key_column_name) ) )
    else:
      columns.append( Column( field_name,
                              sqlalchemy_types[field_type],
                              primary_key=(field_name==entity_class.ID_FIELD) ) )
  if entity_class.ID_FIELD is None:
    columns.append( Column( "id", Integer, primary_key=True ) )
  
  return Table( entity_class.TABLENAME, metadata, *columns )

class Agency(GTFSEntity):
  TABLENAME = "agency"
  FIELDS = (('agency_id',str),
            ('agency_name',str),
	    ('agency_url',str),
	    ('agency_timezone',str),
	    ('agency_lang',str),
	    ('agency_phone',str))
  ID_FIELD = "agency_id"

  def __init__(self, **kwargs):
    GTFSEntity.__init__(self, **kwargs)

  def __repr__(self):
    return "<Agency %s>"%self.agency_id

class ServicePeriod(GTFSEntity):
  TABLENAME = "calendar"
  FIELDS = (('service_id', str),
            ('monday', int),
	    ('tuesday', int),
	    ('wednesday', int),
	    ('thursday', int),
	    ('friday', int),
	    ('saturday', int),
	    ('sunday', int),
	    ('start_date', str),
	    ('end_date',str))
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

class ServiceException(GTFSEntity):
  TABLENAME = "calendar_dates"
  FIELDS = (('service_id', make_gtfs_foreign_key_class(ServicePeriod)),
            ('date', str),
	    ('exception_type', str))
  ID_FIELD = None

  def __repr__(self):
    return "<ServiceException %s %s>"%(self.date, self.exception_type)

class Route(GTFSEntity):
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

class Stop(GTFSEntity):
  TABLENAME = "stops"
  FIELDS = (('stop_id',str),
            ('stop_code',str),
	    ('stop_name',str),
	    ('stop_desc',str),
	    ('stop_lat',str),
	    ('stop_lon',str),
	    ('zone_id',str),
	    ('stop_url',str),
	    ('location_type',str),
	    ('parent_station',str))
  ID_FIELD = "stop_id"

  def __repr__(self):
    return "<Stop %s>"%self.stop_id

class Trip(GTFSEntity):
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

class StopTime(GTFSEntity):
  TABLENAME = "stop_times"
  FIELDS = (('trip_id',make_gtfs_foreign_key_class(Trip)),
            ('arrival_time',str),
	    ('departure_time',str),
	    ('stop_id',make_gtfs_foreign_key_class(Stop)),
	    ('stop_sequence',int),
	    ('stop_headsign',str),
	    ('pickup_type',str),
	    ('drop_off_type',str),
	    ('shape_dist_traveled',str))
  ID_FIELD = None
  
  def __repr__(self):
    return "<StopTime %s %s>"%(self.trip_id,self.departure_time)

class Fare(GTFSEntity):
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

class FareRule(GTFSEntity):
  TABLENAME = "fare_rules"
  FIELDS = (('fare_id',make_gtfs_foreign_key_class(Fare)),
            ('route_id',make_gtfs_foreign_key_class(Route)),
	    ('origin_id',str),
	    ('destination_id',str),
	    ('contains_id',str))
  ID_FIELD = None

class ShapePoint(GTFSEntity):
  TABLENAME = "shapes"
  FIELDS = (('shape_id',str),
            ('shape_pt_lat',str),
	    ('shape_pt_lon',str),
	    ('shape_pt_sequence',int),
	    ('shape_dist_traveled',str))
  ID_FIELD = None

class Frequency(GTFSEntity):
  TABLENAME = "frequencies"
  FIELDS = (('trip_id',make_gtfs_foreign_key_class(Trip)),
            ('start_time',str),
	    ('end_time',str),
	    ('headway_secs',int))
  ID_FIELD = None

  def __repr__(self):
    return "<Frequency %s-%s %s>"%(self.start_time,self.end_time,self.headway_secs)

class Transfer(GTFSEntity):
  TABLENAME = "transfers"
  FIELDS = (('from_stop_id',make_gtfs_foreign_key_class(Stop)),
            ('to_stop_id',make_gtfs_foreign_key_class(Stop)),
	    ('transfer_type',int),
	    ('min_transfer_time',str))
  ID_FIELD = None

metadata = MetaData()
agency_table = table_def_from_entity( Agency, metadata )
routes_table = table_def_from_entity( Route, metadata )
trips_table = table_def_from_entity( Trip, metadata )
stop_times_table = table_def_from_entity( StopTime, metadata )
calendar_table = table_def_from_entity( ServicePeriod, metadata )
calendar_dates_table = table_def_from_entity( ServiceException, metadata )
fare_attributes_table = table_def_from_entity( Fare, metadata )
fare_rules_table = table_def_from_entity( FareRule, metadata )
stops_table = table_def_from_entity( Stop, metadata )
shapes_table = table_def_from_entity( ShapePoint, metadata )
frequencies_table = table_def_from_entity( Frequency, metadata )
transfers_table = table_def_from_entity( Transfer, metadata )

class Record(object):
  def __init__(self,header,row):
    self.header = header
    self.row = [x.strip() for x in row.split(",")]

  def to_dict(self):
    return dict([(fieldname,self.row[fieldindex]) for fieldname,fieldindex in self.header.items()])

  def __repr__(self):
    return repr(self.to_dict())

  def __getitem__(self,name):
    try:
      return self.row[ self.header[name] ]
    except KeyError:
      return None

class Table(object):
  def __init__(self, header, rows):
    split_header = [x.strip() for x in header.split(",")]

    # header is a dict of name->index
    self.header = dict( zip( split_header, range(len(split_header)) ) ) 
    self.rows = rows

  def __repr__(self):
    return "<Table %s>"%self.header

  def __iter__(self):
    return self

  def next(self):
    return Record( self.header, self.rows.next() )

class Feed(object):
  def __init__(self, filename):
    self.filename = filename 
    self.zf = None

    if not os.path.isdir( filename ):
      self.zf = ZipFile( filename )

  def get_rows(self, filename):
    if self.zf:
      return iterdecode( self.zf.read(filename).split("\n"), "utf-8" )
    else:
      return iterdecode( open( os.path.join( self.filename, filename ) ), "utf-8" )

  def get_table(self, filename):
    rows = self.get_rows( filename )
    return Table( rows.next(), rows )

def load(session):

  feed = Feed( "/home/brandon/Desktop/bart.zip" )

  for gtfs_class in (Agency, 
                     #Route, 
		     Stop,
		     Trip, 
		     #StopTime,
		     #ServicePeriod, 
		     #ServiceException, 
		     #Fare,
		     #FareRule,
		     #ShapePoint,
		     Frequency,
		     Transfer,
		     ):

    print "loading %s"%gtfs_class
    
    for record in feed.get_table( gtfs_class.TABLENAME+".txt" ):
      instance = gtfs_class( **record.to_dict() )
      session.add( instance )

  print "commit"
  session.commit()

def cons(ary):
  for i in range(len(ary)-1):
    yield ary[i],ary[i-1]

def query(session):
  counts = {}

  #for agency in session.query(Agency).filter(Agency.agency_id=="BART"):
  #  for route in agency.routes:
  #    print route
  #    for trip in route.trips:
  #      for st1, st2 in cons(trip.stop_times):
  #	  counts[(st1.stop_id,st2.stop_id)] = counts.get((st1.stop_id,st2.stop_id),0)+1

  #print counts

  #for route in session.query(Route).filter(Route.route_id=='01'):
  #  trip = route.trips[0]
  #  for stop_time in trip.stop_times:
  #    print stop_time.stop
  #    print stop_time.stop.stop_lat, stop_time.stop.stop_lon

  #for freq in session.query(Frequency):
  #  print freq
  #  print freq.trip
  #  print freq.trip.route_id

  for transfer in session.query(Transfer):
    print transfer
    print transfer.from_stop, transfer.to_stop

  #for cal in session.query(ServicePeriod):
  #  print cal
  #  print cal.exceptions


if __name__=='__main__':
  engine = create_engine('sqlite:////home/brandon/Desktop/test.db', echo=False)
  metadata.create_all(engine) 
  mapper(Agency, agency_table, properties={'routes':relationship(Route)}) 
  mapper(Route, routes_table, properties={'agency':relationship(Agency),'trips':relationship(Trip),'fare_rules':relationship(FareRule)})
  mapper(Stop, stops_table)
  mapper(Trip, trips_table, properties={'route':relationship(Route),
                                        'stop_times':relationship(StopTime),
					'service_period':relationship(ServicePeriod),
					'frequencies':relationship(Frequency)})
  mapper(StopTime, stop_times_table, properties={'trip':relationship(Trip),'stop':relationship(Stop)})
  mapper(ServicePeriod, calendar_table,properties={'trips':relationship(Trip),'exceptions':relationship(ServiceException)})
  mapper(ServiceException, calendar_dates_table, properties={'calendar':relationship(ServicePeriod)})
  mapper(Fare, fare_attributes_table, properties={'rules':relationship(FareRule)})
  mapper(FareRule, fare_rules_table, properties={'fare':relationship(Fare),'route':relationship(Route)})
  mapper(ShapePoint, shapes_table)
  mapper(Frequency, frequencies_table, properties={'trip':relationship(Trip)})
  mapper(Transfer, transfers_table, properties={"from_stop":relationship(Stop,primaryjoin=transfers_table.c.from_stop_id==stops_table.c.stop_id),
                                                "to_stop":relationship(Stop,primaryjoin=transfers_table.c.to_stop_id==stops_table.c.stop_id)})

  Session = sessionmaker(bind=engine)
  session = Session()

  #load(session)
  query(session)
