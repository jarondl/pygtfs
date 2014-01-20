from __future__ import division, absolute_import, print_function, unicode_literals
from optparse import OptionParser
from loader import load
import os

def main():
    """Script to load GTFS data into a database."""
    
    usage = 'usage: %prog [options] gtfs_file'
    epilog = ('Convert data in gtfs_file into database format. gtfs_file can be '
              'any format supported by gtfs-sql (either a zip file or a '
              'directory containing CSVs).')
    
    parser = OptionParser(usage, epilog=epilog)
    parser.add_option('-o', '--output_filename', dest='output_filename',
                      help='database to write to (default [gtfs_file without extension].db)')

    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error('No gtfs filename supplied')
    gtfs_filename = args[0]

    if options.output_filename:
        output_filename = options.output_filename
    else:
        output_filename = os.path.splitext(gtfs_filename)[0] + '.db'

    load(gtfs_filename, output_filename)

if __name__=='__main__':
    main()
