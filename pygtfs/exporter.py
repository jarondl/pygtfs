from __future__ import division, absolute_import, print_function, unicode_literals

from .schedule import Schedule
from .gtfs_entities import gtfs_all
#from .gtfs_entities import Agency, Stop, Route, Trip, StopTime, Service, ServiceException, Fare, FareRule, ShapePoint, Frequency, Transfer 
import os
import csv
from zipfile import ZipFile

def export_feed(schedule, save_path, filename, zipped=False):
    """Export feeds either to a directory as a series of text files or to a
    zip file
    
    :param schedule: The schedule object
    :type schedule: Schedule
    :param save_path: The path where the directory or zip file should be created
    :type save_path: str
    :param filename: The name of the directory or zip file to be created
    :type filename: str
    :param zipped: Export as a zipped file? (default=False)
    :type zipped: bool import 
    """
    
    # Build the full path
    file_path = os.path.join(save_path,filename)
    if zipped: file_path += ".zip"
    verify_path(file_path)
    
    # Create the dir
    os.mkdir(file_path)
    
    # Export each table
    for gtfs_class in gtfs_all:
        gtfs_filename = os.path.join(file_path, gtfs_class.__tablename__ + '.txt')
        print('Exporting %s' % gtfs_filename)
        fh = open(gtfs_filename, 'wb')
        outFile = csv.writer(fh)
        outFile.writerow("table headers here")
        outFile.writerow("table data here")
        #outFile.writerow(gtfs_class)
        fh.close()
        
    
def export_shapefile(save_path, filename, trip_id):
    """Future enhancement to export a trip shapefile from a feed if the feed
    has a shapes.txt file
    :param save_path: The path where the shapefile should be created
    :type save_path: str
    :param filename: The name of the shapefile to be created
    :type filename: str
    :param trip_id: The trip ID to be exported
    :type trip_id: str
    """
    pass

def verify_path(path):
    if not os.path.isdir(os.path.dirname(path)):
        raise IOError('%s is not a valid directory' % os.path.dirname(path))
    if os.path.isdir(path) or os.path.isfile(path): raise IOError('%s already exists' % path)