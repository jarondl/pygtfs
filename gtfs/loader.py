from __future__ import print_function
from entity import *
from schedule import Schedule
from sqlalchemy.orm.exc import UnmappedInstanceError
import feed
import sys

def load(feed_filename, db_connection=":memory:", strip_fields=True,
         commit_chunk=500, **kwargs):
    if 'db_filename' in kwargs:
        db_connection = kwargs['db_filename']
    schedule = Schedule(db_connection)
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
    agency_id = None
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
                    record_stripped = {}
                    for key in record:
                        record_stripped[key.strip()] = record[key].strip()
                    record = record_stripped
                if gtfs_class is Agency:
                    if 'agency_id' not in record or \
                            not record['agency_id'].strip():
                        record['agency_id'] = record['agency_name'].lower()
                    if agency_id is not None and record['agency_id'] != agency_id:
                        raise Exception('Loading multiple agencies at the same time not supported')
                    agency_id = record['agency_id']
                record['agency_id'] = agency_id
                instance = gtfs_class(**record)
                schedule.session.merge(instance)
                if i % commit_chunk == 0 and i > 0:
                    schedule.session.commit()
                    sys.stdout.write('.')
                    sys.stdout.flush()
        print('%d record%s committed.' % ((i+1), '' if i == 0 else 's'))
        schedule.session.commit()

    print('Complete.')
    return schedule