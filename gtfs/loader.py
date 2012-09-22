from entity import *
from schedule import Schedule
import feed
import sqlalchemy.orm.exc
import sys

def load(feed_filename, db_filename=":memory:"):
    
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

        print "Loading GTFS data for %s" % gtfs_class
        gtfs_filename = gtfs_class.table_name + '.txt'
     
        try:
            for i, record in enumerate(fd.get_table(gtfs_filename)):
                if any(record.to_dict().values()):
                    if i % 500 == 0 and i > 0:
                        sys.stdout.write(".")
                        sys.stdout.flush()
                        schedule.session.commit()
                    instance = gtfs_class(**record.to_dict())
                    schedule.session.add(instance)
            print
        except sqlalchemy.orm.exc.UnmappedInstanceError as e:
            if gtfs_class.gtfs_required:
                raise Exception("Error: could not find %s" % gtfs_filename)
            elif no_calendar is True and gtfs_class == ServiceException:
                raise Exception("Error: could not find either %s or %s" % \
                                (gtfs_filename, Service.table_name + '.txt'))
            else:
                if gtfs_class == Service:
                    no_calendar = True
                print "No file %s but not mandatory, continuing..." % gtfs_filename
                continue

    schedule.session.commit()
    return schedule