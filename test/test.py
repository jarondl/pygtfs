import sys
sys.path.append( ".." )

from gtfsparser.loader import load
from gtfsparser import metadata
from gtfsparser.schedule import Schedule

if __name__=='__main__':
  #schedule = load( metadata, "/home/brandon/Desktop/bart.zip", "/home/brandon/Desktop/test.db" )

  schedule = Schedule( "/home/brandon/Desktop/test.db" )
  print schedule.routes
  print schedule.agencies

