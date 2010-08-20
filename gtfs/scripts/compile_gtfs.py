from ..loader import load
from ..schedule import Schedule

from optparse import OptionParser
import os

def main():
  usage = "usage: %prog [options] gtfs_filename"
  parser = OptionParser(usage)
  parser.add_option( "-o", "--output_filename", dest="output_filename" )

  options, args = parser.parse_args()

  if len(args) != 1:
    parser.error( "No gtfs filename supplied" )

  gtfs_filename = args[0]

  if options.output_filename:
    output_filename = options.output_filename
  else:
    output_filename = os.path.splitext( gtfs_filename )[0]+".db"

  load( gtfs_filename, output_filename )

if __name__=='__main__':
  main()
