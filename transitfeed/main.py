import sqlalchemy
from sqlalchemy.orm import relationship

from entity import *
from gtfs import GTFSForeignKey
import feed

def table_def_from_entity(entity_class, metadata):
  sqlalchemy_types = {str:sqlalchemy.String,int:sqlalchemy.Integer}
  columns = []
  for field_name,field_type in entity_class.FIELDS:
    if issubclass(field_type, GTFSForeignKey):
      foreign_key_column_name = field_type._cls.TABLENAME+"."+field_type._cls.ID_FIELD
      columns.append( sqlalchemy.Column( field_name, sqlalchemy.String, sqlalchemy.ForeignKey(foreign_key_column_name) ) )
    else:
      columns.append( sqlalchemy.Column( field_name,
                              sqlalchemy_types[field_type],
                              primary_key=(field_name==entity_class.ID_FIELD) ) )
  if entity_class.ID_FIELD is None:
    columns.append( sqlalchemy.Column( "id", sqlalchemy.Integer, primary_key=True ) )
  
  return sqlalchemy.Table( entity_class.TABLENAME, metadata, *columns )

def create_and_map_tables(metadata):
  # create the tables
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

  # map the tables
  sqlalchemy.orm.mapper(Agency, agency_table, properties={'routes':relationship(Route)}) 
  sqlalchemy.orm.mapper(Route, routes_table, properties={'agency':relationship(Agency),'trips':relationship(Trip),'fare_rules':relationship(FareRule)})
  sqlalchemy.orm.mapper(Stop, stops_table)
  sqlalchemy.orm.mapper(Trip, trips_table, properties={'route':relationship(Route),
                                        'stop_times':relationship(StopTime),
					'service_period':relationship(ServicePeriod),
					'frequencies':relationship(Frequency)})
  sqlalchemy.orm.mapper(StopTime, stop_times_table, properties={'trip':relationship(Trip),'stop':relationship(Stop)})
  sqlalchemy.orm.mapper(ServicePeriod, calendar_table,properties={'trips':relationship(Trip),'exceptions':relationship(ServiceException)})
  sqlalchemy.orm.mapper(ServiceException, calendar_dates_table, properties={'calendar':relationship(ServicePeriod)})
  sqlalchemy.orm.mapper(Fare, fare_attributes_table, properties={'rules':relationship(FareRule)})
  sqlalchemy.orm.mapper(FareRule, fare_rules_table, properties={'fare':relationship(Fare),'route':relationship(Route)})
  sqlalchemy.orm.mapper(ShapePoint, shapes_table)
  sqlalchemy.orm.mapper(Frequency, frequencies_table, properties={'trip':relationship(Trip)})
  sqlalchemy.orm.mapper(Transfer, transfers_table, properties={"from_stop":relationship(Stop,primaryjoin=transfers_table.c.from_stop_id==stops_table.c.stop_id),
                                                "to_stop":relationship(Stop,primaryjoin=transfers_table.c.to_stop_id==stops_table.c.stop_id)})

def load(session):

  fd = feed.Feed( "/home/brandon/Desktop/bart.zip" )

  for gtfs_class in (Agency, 
                     Route, 
		     Stop,
		     Trip, 
		     StopTime,
		     ServicePeriod, 
		     ServiceException, 
		     Fare,
		     FareRule,
		     ShapePoint,
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
  metadata = sqlalchemy.MetaData()

  create_and_map_tables(metadata)

  engine = sqlalchemy.create_engine('sqlite:////home/brandon/Desktop/test.db', echo=False)
  metadata.create_all(engine) 

  Session = sqlalchemy.orm.sessionmaker(bind=engine)
  session = Session()

  load(session)
  query(session)
