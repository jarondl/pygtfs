import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
import os
from codecs import iterdecode
from zipfile import ZipFile
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

metadata = MetaData()
agency_table = Table('agency', metadata,
    Column('agency_id', String, primary_key=True),
    Column('agency_name', String),
    Column('agency_url', String),
    Column('agency_timezone', String),
    Column('agency_lang', String),
    Column('agency_phone', String)
)

class Agency(Base):

   agency_id = Column(String, primary_key=True)
   agency_name = Column(String)
   agency_url = Column(String)
   agency_timezone = Column(String)
   agency_lang = Column(String)
   agency_phone = Column(String)

  def __init__(self, agency_id,
                       agency_name,
		       agency_url,
		       agency_timezone,
		       agency_lang,
		       agency_phone):
    self.agency_id = agency_id
    self.agency_name = agency_name
    self.agency_url = agency_url
    self.agency_timezone = agency_timezone
    self.agency_lang = agency_lang
    self.agency_phone = agency_phone

class Record(object):
  def __init__(self,header,row):
    self.header = header
    self.row = [x.strip() for x in row.split(",")]

  def __repr__(self):
    return repr(dict(zip(self.header.keys(), self.row)))

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

if __name__=='__main__':
  engine = create_engine('sqlite:////home/brandon/Desktop/test.db', echo=True)
  metadata.create_all(engine) 
  mapper(Agency, agency_table) 
  Session = sessionmaker(bind=engine)
  session = Session()

  feed = Feed( "/home/brandon/Desktop/bart.zip" )

  for record in feed.get_table( "agency.txt" ):
    agency = Agency( record['agency_id'],
                     record['agency_name'],
		     record['agency_url'],
		     record['agency_timezone'],
		     record['agency_lang'],
		     record['agency_phone'] )
    session.add( agency )

  session.commit()
