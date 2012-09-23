from sqlalchemy import Column, Table
from sqlalchemy.orm import mapper, relationship
from unmapped_entities import *

def table_def_from_entity(entity_class, metadata):
    """Construct an SQLAlchemy Table from one of the subclasses of Entity in 
    unmapped_entities. This is used by create_and_map_tables in a "classical"-
    style SQLAlchemy mapping. 
    """
    
    columns = []
    for field in entity_class.fields:
        if field.foreign_key is not None:
            columns.append(Column(field.name, field.column_type, 
                                  ForeignKey(field.foreign_key), 
                                  primary_key=field.primary_key,
                                  index=True))
        else:
            columns.append(Column(field.name, field.column_type,
                                  primary_key=field.primary_key))
    return Table(entity_class.table_name, metadata, *columns)

def create_and_map_tables(metadata):
    """For each of the subclasses of Entity in unmapped_entities, construct
    the table and the mapping into metadata. 
    """
    
    # create the tables
    agency_table = table_def_from_entity(Agency, metadata)
    stops_table = table_def_from_entity(Stop, metadata)
    routes_table = table_def_from_entity(Route, metadata)
    calendar_table = table_def_from_entity(Service, metadata)
    calendar_dates_table = table_def_from_entity(ServiceException, metadata)
    trips_table = table_def_from_entity(Trip, metadata)
    stop_times_table = table_def_from_entity(StopTime, metadata)
    fare_attributes_table = table_def_from_entity(Fare, metadata)
    fare_rules_table = table_def_from_entity(FareRule, metadata)
    shapes_table = table_def_from_entity(ShapePoint, metadata)
    frequencies_table = table_def_from_entity(Frequency, metadata)
    transfers_table = table_def_from_entity(Transfer, metadata)
    feed_info_table = table_def_from_entity(FeedInfo, metadata)

    # map the tables
    mapper(Agency, agency_table)
    mapper(Stop, stops_table)
    mapper(Route, routes_table, 
           properties={'agency': relationship(Agency, backref='routes')})
    mapper(Service, calendar_table)
    mapper(ServiceException, calendar_dates_table, 
           properties={'service': relationship(Service, backref='exceptions')})
    mapper(Trip, trips_table, 
           properties={'route': relationship(Route, backref='trips'),
					   'service': relationship(Service, backref='trips'),
					   'stop_times': relationship(StopTime, order_by=stop_times_table.c.stop_sequence)})
    mapper(StopTime, stop_times_table, 
           properties={'trip': relationship(Trip),
                       'stop': relationship(Stop, backref='stop_times')})
    mapper(Fare, fare_attributes_table)
    mapper(FareRule, fare_rules_table, 
           properties={'fare': relationship(Fare, backref='rules'),
                       'route': relationship(Route, backref='fare_rules')})
    mapper(ShapePoint, shapes_table)
    mapper(Frequency, frequencies_table, 
           properties={'trip': relationship(Trip, backref='frequencies')})
    mapper(Transfer, transfers_table, 
           properties={'from_stop': relationship(Stop, 
                                                 primaryjoin=transfers_table.c.from_stop_id == stops_table.c.stop_id,
                                                 backref="transfers_away"),
                       'to_stop': relationship(Stop,
                                               primaryjoin=transfers_table.c.to_stop_id == stops_table.c.stop_id,
                                               backref="transfers_from")})
    mapper(FeedInfo, feed_info_table)