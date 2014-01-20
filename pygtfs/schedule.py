from __future__ import division, absolute_import, print_function, unicode_literals

import sqlalchemy
import sqlalchemy.orm

from .gtfs_entities import gtfs_all, Feed

class Schedule:
    """Represents a full GTFS data set.

    Note that we are adding properties dynamically after the definition"""
    
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.db_filename = None
        if '://' not in db_connection:
            self.db_connection = 'sqlite:///%s' % self.db_connection
        if self.db_connection.startswith('sqlite'):
            self.db_filename = self.db_connection
        self.engine = sqlalchemy.create_engine(self.db_connection, echo=False)
        Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = Session()


    def create_tables(self, metadata):
        metadata.create_all(self.engine) 

    def drop_feed(self, feed_id):
        self.session.query(Feed).filter(Feed.feed_id == feed_id).delete()
        self.session.commit()

def _meta_query_all(entity):
    def _query_all(instance_self):
        return instance_self.session.query(entity).all()
    return property(_query_all)

def _meta_query_by_id(entity):
    def _query_by_id(instance_self, id):
        return instance_self.session.query(entity).filter(entity.id == id).all()
    return _query_by_id

for entity in (gtfs_all + [Feed]):
    setattr(Schedule, entity._plural_name_, _meta_query_all(entity))
    if hasattr(entity, 'id'):
        setattr(Schedule, entity._plural_name_ + "_by_id", _meta_query_by_id(entity))    
