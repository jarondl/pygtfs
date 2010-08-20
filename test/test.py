import sys
sys.path.append( ".." )

from gtfsparser.loader import load
from gtfsparser import metadata
from gtfsparser.schedule import Schedule

if __name__=='__main__':
  schedule = load( metadata, "data/sample-feed.zip" )

  print schedule.routes
  for trip in schedule.routes[0].trips:
    print trip
    for stop_time in trip.stop_times:
      print stop_time
    for frequency in trip.frequencies:
      print frequency
  for service_period in schedule.service_periods:
    print service_period
  print schedule.agencies

  #schedule = Schedule( "/home/brandon/Desktop/test.db" )
  #print schedule.routes
  #print schedule.agencies

