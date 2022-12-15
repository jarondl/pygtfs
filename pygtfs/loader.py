from __future__ import (division, absolute_import, print_function,
                        unicode_literals)

import sys
from datetime import date

import six

from . import feed
from .exceptions import PygtfsException
from .gtfs_entities import (Feed, gtfs_required,
                            Translation, Stop, Trip, ShapePoint, _stop_translations,
                            _trip_shapes, gtfs_calendar, gtfs_all)


def list_feeds(schedule):
    for (i, a_feed) in enumerate(schedule.feeds):
        print("{0}. id {1.feed_id}, name {1.feed_name}, "
              "loaded on {1.feed_append_date}".format(i, a_feed))


def delete_feed(schedule, feed_filename, interactive=False):

    feed_name = feed.derive_feed_name(feed_filename)
    feeds_with_name = schedule.session.query(Feed).filter(Feed.feed_name == feed_name).all()
    delete_all = not interactive
    for matching_feed in feeds_with_name:
        if not delete_all:
            print("Found feed ({0.feed_id}) named {0.feed_name} loaded on {0.feed_append_date}".format(matching_feed))
            ans = ""
            while ans not in ("K", "O", "A"):
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
                chunk_size=5000, agency_id_override=None, ignore_failures=True):

    fd = feed.Feed(feed_filename, strip_fields)

    gtfs_tables = {}
    for gtfs_class in gtfs_all:
        print('Loading GTFS data for %s:' % gtfs_class)
        gtfs_filename = gtfs_class.__tablename__ + '.txt'

        try:
            # We ignore the feed supplied feed id, because we create our own
            # later.
            gtfs_tables[gtfs_class] = fd.read_table(gtfs_filename,
                                                    set(c.name for c in gtfs_class.__table__.columns) - {'feed_id'})
        except (KeyError, IOError):
            if gtfs_class in gtfs_required:
                raise IOError('Error: could not find %s' % gtfs_filename)

    if len(set(gtfs_tables) & gtfs_calendar) == 0:
        raise PygtfsException('Must have Calendar.txt or Calendar_dates.txt')

    # create new feed
    feed_entry = Feed(feed_name=fd.feed_name, feed_append_date=date.today())
    schedule.session.add(feed_entry)
    schedule.session.flush()
    feed_id = feed_entry.feed_id
    for gtfs_class in gtfs_all:
        if gtfs_class not in gtfs_tables:
            continue
        gtfs_table = gtfs_tables[gtfs_class]

        skipped_records = 0
        read_records = 0
        for i, record in enumerate(gtfs_table):
            if not record:
                # Empty row.
                continue

            try:
                instance = gtfs_class(feed_id=feed_id, **record._asdict())
                schedule.session.add(instance)
                read_records += 1
            except:
                skipped_records += 1
                print(f"Failure while writing {record}")
                if not ignore_failures:
                    raise
            if i % chunk_size == 0 and i > 0:
                schedule.session.flush()
                sys.stdout.write('.')
                sys.stdout.flush()
        print(f'{read_records} records read for {gtfs_class}')
        print(f'{skipped_records} records skipped for {gtfs_class}')
    schedule.session.flush()
    schedule.session.commit()
    # load many to many relationships
    if Translation in gtfs_tables:
        print('Mapping translations to stops')
        q = (schedule.session.query(
                Stop.feed_id.label('stop_feed_id'),
                Translation.feed_id.label('translation_feed_id'),
                Stop.stop_id.label('stop_id'),
                Translation.trans_id.label('trans_id'),
                Translation.lang.label('lang'))
            .filter(Stop.feed_id==feed_id)
            .filter(Translation.feed_id==feed_id)
            .filter(Stop.stop_name==Translation.trans_id)
            )
        upd = _stop_translations.insert().from_select(
                ['stop_feed_id', 'translation_feed_id', 'stop_id', 'trans_id', 'lang'], q)
        schedule.session.execute(upd)
    if ShapePoint in gtfs_tables:
        print('Mapping shapes to trips')
        q = (schedule.session.query(
                Trip.feed_id.label('trip_feed_id'),
                ShapePoint.feed_id.label('shape_feed_id'),
                Trip.trip_id.label('trip_id'),
                ShapePoint.shape_id.label('shape_id'),
                ShapePoint.shape_pt_sequence.label('shape_pt_sequence'))
            .filter(Trip.feed_id==feed_id)
            .filter(ShapePoint.feed_id==feed_id)
            .filter(ShapePoint.shape_id==Trip.shape_id)
            )
        upd = _trip_shapes.insert().from_select(
                ['trip_feed_id', 'shape_feed_id', 'trip_id', 'shape_id', 'shape_pt_sequence'], q)
        schedule.session.execute(upd)
    schedule.session.commit()

    print('Complete.')
    return schedule
