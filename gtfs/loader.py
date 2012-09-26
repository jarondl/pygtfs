from __future__ import print_function
from entity import *
from schedule import Schedule
from sqlalchemy.orm.exc import UnmappedInstanceError
import feed
import sys

def load(feed_filename, db_filename=":memory:", strip_fields=True, 
         commit_chunk=500):
    
    schedule = Schedule(db_filename) 
    schedule.create_tables(Entity.metadata)
    fd = feed.Feed(feed_filename)
    
    gtfs_classes = (Agency,
                    Stop,
                    Route,
                    Service,
                    ServiceException,
                    Trip, 
                    StopTime,
                    Fare,
                    FareRule,
                    ShapePoint,
                    Frequency,
                    Transfer,
                    FeedInfo,
                    )

    no_calendar = False
    for gtfs_class in gtfs_classes:

        print('Loading GTFS data for %s:' % gtfs_class)
        gtfs_filename = gtfs_class.table_name + '.txt'
     
        try:
            gtfs_table = fd.read_table(gtfs_filename)
        except (KeyError, IOError) as e:
            if gtfs_class.gtfs_required:
                raise IOError('Error: could not find %s' % gtfs_filename)
            elif no_calendar is True and gtfs_class == ServiceException:
                raise IOError('Error: could not find either %s or %s' % \
                              (gtfs_filename, Service.table_name + '.txt'))
            else:
                if gtfs_class == Service:
                    # OK if there's no calendar file, but then later ensure 
                    # that there is a calendar_dates file
                    no_calendar = True
                print('File %s not present but not mandatory, continuing.' % \
                      gtfs_filename)
                continue
        
        for i, record in enumerate(gtfs_table):
            if len(record) > 0:
                if strip_fields is True:
                    for key in record:
                        record[key] = record[key].strip()
                instance = gtfs_class(**record)
                schedule.session.add(instance)
                if i % commit_chunk == 0 and i > 0:
                    schedule.session.commit()
                    sys.stdout.write('.')
                    sys.stdout.flush()
        print('%d record%s committed.' % ((i+1), '' if i == 0 else 's'))
        schedule.session.commit()

    print('Complete.')
    return schedule