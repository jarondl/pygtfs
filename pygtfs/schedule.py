from __future__ import (division, absolute_import, print_function,
                        unicode_literals)

import sqlalchemy
import sqlalchemy.orm

from .gtfs_entities import gtfs_all, Feed, Base


class Schedule:
    """Represents the full database.

    The schedule is the most important object in pygtfs. It represents the
    entire dataset. Most of the properties come straight from the gtfs
    reference. Two of them were renamed: calendar is called `services`, and
    calendar_dates `service_exceptions`. One addition is the `feeds` table,
    which is here to support more than one feed in a database.

    Each of the properties is a list created upon access by sqlalchemy. Then,
    each element of the list as attributes following the gtfs reference. In
    addition, if they are related to another table, this can also be accessed
    by attribute.

    :param db_conection: Either a sqlalchemy database url or a filename to be used with sqlite.

    """

    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.db_filename = None
        if '://' not in db_connection:
            self.db_connection = 'sqlite:///%s' % self.db_connection
        if self.db_connection.startswith('sqlite'):
            self.db_filename = self.db_connection
        self.engine = sqlalchemy.create_engine(self.db_connection)
        Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)

    def drop_feed(self, feed_id):
        """ Delete a feed from a database by feed id"""
        # the following does not cascade unfortunatly.
        # self.session.query(Feed).filter(Feed.feed_id == feed_id).delete()
        feed = self.session.query(Feed).get(feed_id)
        self.session.delete(feed)
        self.session.commit()


def _meta_query_all(entity, docstring=None):
    def _query_all(instance_self):
        """ A list generated on access """
        return instance_self.session.query(entity).all()

    if docstring is not None:
        _query_all.__doc__ = docstring
    return property(_query_all)


def _meta_query_by_id(entity, docstring=None):
    def _query_by_id(self, id):
        """ A function that returns a list of entries with matching ids """
        return self.session.query(entity).filter(entity.id == id).all()
    if docstring is not None:
        _query_by_id.__doc__ = docstring
    return _query_by_id


def _meta_query_raw(entity, docstring=None):
    def _query_raw(instance_self):
        """
            A raw sqlalchemy query object that the user can then manipulate
            manually
        """
        return instance_self.session.query(entity)

    if docstring is not None:
        _query_raw.__doc__ = docstring
    return property(_query_raw)


for entity in (gtfs_all + [Feed]):
    entity_doc = "A list of :py:class:`pygtfs.gtfs_entities.{0}` objects".format(entity.__name__)
    entity_raw_doc = ("A :py:class:`sqlalchemy.orm.Query` object to fetch "
                      ":py:class:`pygtfs.gtfs_entities.{0}` objects"
                      .format(entity.__name__))
    entity_by_id_doc = "A list of :py:class:`pygtfs.gtfs_entities.{0}` objects with matching id".format(entity.__name__)
    setattr(Schedule, entity._plural_name_, _meta_query_all(entity, entity_doc))
    setattr(Schedule, entity._plural_name_ + "_query",
            _meta_query_raw(entity, entity_raw_doc))
    if hasattr(entity, 'id'):
        setattr(Schedule, entity._plural_name_ + "_by_id", _meta_query_by_id(entity, entity_by_id_doc))    
