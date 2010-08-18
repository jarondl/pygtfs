import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
import os
from codecs import iterdecode
from zipfile import ZipFile
from sqlalchemy.orm import sessionmaker, relationship

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
        setattr( self, attrname, attrtype( kwargs[attrname] ) )


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

class Trip(GTFSEntity):
  TABLENAME = "trips"
  FIELDS = (('route_id',make_gtfs_foreign_key_class(Route)),
            ('service_id',str),
	    ('trip_id',str),
	    ('trip_headsign',str),
	    ('trip_short_name',str),
	    ('direction_id',str),
	    ('block_id',str),
	    ('shape_id',str))
  ID_FIELD = "trip_id"

  def __repr__(self):
    return "<Trip %s>"%self.trip_id

metadata = MetaData()
agency_table = table_def_from_entity( Agency, metadata )
routes_table = table_def_from_entity( Route, metadata )
trips_table = table_def_from_entity( Trip, metadata )

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
  agency_table = feed.get_table( "agency.txt" )

  for record in feed.get_table( "agency.txt" ):
    agency = Agency( **record.to_dict() )
    session.add( agency )

  for record in feed.get_table( "routes.txt" ):
    route = Route( **record.to_dict() )
    session.add( route )

  for record in feed.get_table( "trips.txt" ):
    trip = Trip( **record.to_dict() )
    session.add( trip )

  session.commit()

def query(session):
  for agency in session.query(Agency).filter(Agency.agency_id=="BART"):
    print agency.routes[0].trips

  #for route in session.query(Route):
  #  print route

if __name__=='__main__':
  engine = create_engine('sqlite:////home/brandon/Desktop/test.db', echo=True)
  metadata.create_all(engine) 
  mapper(Agency, agency_table, properties={'routes':relationship(Route)}) 
  mapper(Route, routes_table, properties={'agency':relationship(Agency),'trips':relationship(Trip)})
  mapper(Trip, trips_table, properties={'route':relationship(Route)})
  Session = sessionmaker(bind=engine)
  session = Session()

  #load(session)
  query(session)
