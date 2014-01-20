from __future__ import division, absolute_import, print_function, unicode_literals

from itertools import chain
import sys

from sqlalchemy.orm.exc import UnmappedInstanceError

from .gtfs_entities import Feed, Service, ServiceException, Base, gtfs_required, gtfs_all
from .schedule import Schedule
from . import feed


def load(feed_filename, db_connection=":memory:", strip_fields=True,
         commit_chunk=500, drop_feed=False, agency_id_override=None):

    schedule = Schedule(db_connection)
    schedule.create_tables(Base.metadata)
    fd = feed.Feed(feed_filename, strip_fields)

    gtfs_tables = {}
    no_calendar = False
    for gtfs_class in gtfs_all:
        print('Loading GTFS data for %s:' % gtfs_class)
        gtfs_filename = gtfs_class.__tablename__ + '.txt'
     
        try:
            gtfs_tables[gtfs_class] = fd.read_table(gtfs_filename)
        except (KeyError, IOError) as e:
            if gtfs_class in gtfs_required:
                raise IOError('Error: could not find %s' % gtfs_filename)
    assert (Service in gtfs_tables) or (ServiceException in gtfs_tables) , "Must have Calendar.txt or Calendar_dates.txt"

    if drop_feed:
        pass

    # create new feed
    feed_entry = Feed(feed_name = fd.feed_name)
    schedule.session.add(feed_entry)
    schedule.session.commit()
    feed_id = feed_entry.feed_id
    
    for gtfs_class in gtfs_all:
        if gtfs_class not in gtfs_tables:
            continue
        gtfs_table = gtfs_tables[gtfs_class]
        for i, record in enumerate(gtfs_table):
            if len(record) > 0:
                instance = gtfs_class(feed_id = feed_id, **record._asdict())
                schedule.session.add(instance)
                if i % commit_chunk == 0 and i > 0:
                    if not drop_feed:
                        schedule.session.commit()
                    sys.stdout.write('.')
                    sys.stdout.flush()
        print('%d record%s committed from %s.' % ((i+1), '' if i == 0 else 's', gtfs_class))
        if not drop_feed:
            schedule.session.commit()
    schedule.session.commit()

    print('Complete.')
    return schedule
