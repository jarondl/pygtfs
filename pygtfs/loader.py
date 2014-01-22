from __future__ import division, absolute_import, print_function, unicode_literals

from itertools import chain
from datetime import date
import sys

from sqlalchemy.orm.exc import UnmappedInstanceError
import six

from .gtfs_entities import Feed, Service, ServiceException, Base, gtfs_required, gtfs_all
from . import feed

def list_feeds(schedule):

    for (i, a_feed) in enumerate(schedule.feeds):
        print("{0}. id {1.feed_id}, name {1.feed_name}, loaded on {1.feed_append_date}".format(i, a_feed))

def delete_feed(schedule, feed_filename, interactive=False):

    feed_name = feed.derive_feed_name(feed_filename)
    feeds_with_name = schedule.session.query(Feed).filter(Feed.feed_name == feed_name).all()
    delete_all = not interactive
    for matching_feed in feeds_with_name:
        if not delete_all:
            print("Found feed ({0.feed_id}) named {0.feed_name} loaded on {0.feed_append_date}".format(matching_feed))
            ans = ""
            while ans not in ("K","O","A"):
                ans = six.moves.input("(K)eep / (O)verwrite / overwrite (A)ll ? ").upper()
            if ans == "K":
                continue
            if ans == "A":
                delete_all = True
        # you get here if ans is A or O, and if delete_all
        schedule.drop_feed(matching_feed.feed_id)

def overwrite_feed(schedule, feed_filename, *args, **kwargs):
    interactive = kwargs.pop('interactive', False)
    delete_feed(schedule, feed_filename, interactive=interactive)
    append_feed(schedule, feed_filename, *args, **kwargs)
    

def append_feed(schedule, feed_filename, strip_fields=True,
         chunk_size=5000, agency_id_override=None):

    fd = feed.Feed(feed_filename, strip_fields)

    gtfs_tables = {}
    for gtfs_class in gtfs_all:
        print('Loading GTFS data for %s:' % gtfs_class)
        gtfs_filename = gtfs_class.__tablename__ + '.txt'
 
        try:
            gtfs_tables[gtfs_class] = fd.read_table(gtfs_filename)
        except (KeyError, IOError) as e:
            if gtfs_class in gtfs_required:
                raise IOError('Error: could not find %s' % gtfs_filename)

    assert (Service in gtfs_tables) or (ServiceException in gtfs_tables) , "Must have Calendar.txt or Calendar_dates.txt"


    # create new feed
    feed_entry = Feed(feed_name = fd.feed_name, feed_append_date= date.today())
    schedule.session.add(feed_entry)
    schedule.session.flush()
    feed_id = feed_entry.feed_id
    
    for gtfs_class in gtfs_all:
        if gtfs_class not in gtfs_tables:
            continue
        gtfs_table = gtfs_tables[gtfs_class]
        for i, record in enumerate(gtfs_table):
            try:
                instance = gtfs_class(feed_id = feed_id, **record._asdict())
            except:
                print("Failure while writing {0}".format(record))
                raise
            schedule.session.add(instance)
            if i % chunk_size == 0 and i > 0:
                schedule.session.flush()
                sys.stdout.write('.')
                sys.stdout.flush()
        print('%d record%s read for %s.' % ((i+1), '' if i == 0 else 's', gtfs_class))
    schedule.session.commit()

    print('Complete.')
    return schedule
