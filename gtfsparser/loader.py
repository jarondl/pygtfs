from schedule import Schedule
import feed
from entity import *

def load(metadata, feed_filename, db_filename=":memory:"):
  schedule = Schedule( db_filename ) 
  schedule.create_tables(metadata)
  
  fd = feed.Feed( feed_filename )

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
      schedule.session.add( instance )

  print "commit"
  schedule.session.commit()

  return schedule
