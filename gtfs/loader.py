from __future__ import print_function
from entity import *
from schedule import Schedule
from sqlalchemy.orm.exc import UnmappedInstanceError
import feed
import sys

def drop_then_load(*args, **kwargs):
    kwargs['drop_feed'] = True
    load(*args, **kwargs)

def load(feed_filename, db_connection=":memory:", strip_fields=True,
         commit_chunk=500, drop_feed=False, agency_id_override=None, **kwargs):
    if 'db_filename' in kwargs:
        db_connection = kwargs['db_filename']
    schedule = Schedule(db_connection)
    schedule.create_tables(Entity.metadata)
    fd = feed.Feed(feed_filename, strip_fields)
    
    gtfs_classes = [Agency,
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
                    ]
    gtfs_tables = {}

    no_calendar = False
    for gtfs_class in gtfs_classes:
        print('Loading GTFS data for %s:' % gtfs_class)
        gtfs_filename = gtfs_class.table_name + '.txt'
     
        try:
            gtfs_tables[gtfs_class] = fd.read_table(gtfs_filename)
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

    if drop_feed:
        # reversed so we don't trip-up on foreign key constraints
        for gtfs_class in reversed(gtfs_classes):
            schedule.session.query(gtfs_class).\
                filter(gtfs_class.feed_name==fd.feed_name).\
                delete()
    for gtfs_class in gtfs_classes:
        if gtfs_class not in gtfs_tables:
            continue
        gtfs_table = gtfs_tables[gtfs_class]
        for i, record in enumerate(gtfs_table):
            if len(record) > 0:
                instance = gtfs_class(feed_name=fd.feed_name, **record._asdict())
                schedule.session.add(instance)
                if i % commit_chunk == 0 and i > 0:
                    if not drop_feed:
                        schedule.session.commit()
                    sys.stdout.write('.')
                    sys.stdout.flush()
        print('%d record%s committed.' % ((i+1), '' if i == 0 else 's'))
        if not drop_feed:
            schedule.session.commit()
    schedule.session.commit()

    print('Complete.')
    return schedule
