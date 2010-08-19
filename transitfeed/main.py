import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql.expression import ColumnElement

from entity import *
from gtfs import GTFSForeignKey
import feed

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

def load(session):

  fd = feed.Feed( "/home/brandon/Desktop/bart.zip" )

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
    
    for record in fd.get_table( gtfs_class.TABLENAME+".txt" ):
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

  load(session)
  query(session)
