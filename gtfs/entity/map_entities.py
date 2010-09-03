import sqlalchemy
from sqlalchemy.orm import relationship
from unmapped_entities import *
from .. import types

class BooleanType(sqlalchemy.types.TypeDecorator):
  impl = sqlalchemy.types.Integer

  def process_bind_param( self, value, dialect ):
    return int(value)

  def process_result_value( self, value, dialect ):
    return types.Boolean( value )

class TimeType(sqlalchemy.types.TypeDecorator):
  impl = sqlalchemy.types.Integer

  def process_bind_param( self, value, dialect ):
    return value.val if value else None

  def process_result_value( self, value, dialect ):
    return types.Time( value ) if value else None

class DateType(sqlalchemy.types.TypeDecorator):
  impl = sqlalchemy.types.Integer

  def process_bind_param( self, value, dialect ):
    return value.val.toordinal() if value else None

  def process_result_value( self, value, dialect ):
    return types.Date( value ) if value else None

def table_def_from_entity(entity_class, metadata):
  sqlalchemy_types = {str:sqlalchemy.String,
                      int:sqlalchemy.Integer,
		      float:sqlalchemy.Float,
		      types.Boolean:BooleanType,
		      types.Time:TimeType,
		      types.Date:DateType}
  columns = []
  for field_name,field_type in entity_class.FIELDS:
    if issubclass(field_type, types.ForeignKey):
      foreign_key_column_name = field_type._cls.TABLENAME+"."+field_type._cls.ID_FIELD
      columns.append( sqlalchemy.Column( field_name, sqlalchemy.String, sqlalchemy.ForeignKey(foreign_key_column_name) ) )
    else:
      columns.append( sqlalchemy.Column( field_name,
                              sqlalchemy_types[field_type],
                              primary_key=(field_name==entity_class.ID_FIELD) ) )
  if entity_class.ID_FIELD is None:
    columns.append( sqlalchemy.Column( "id", sqlalchemy.Integer, primary_key=True ) )
  
  return sqlalchemy.Table( entity_class.TABLENAME, metadata, *columns )

def create_and_map_tables(metadata):
  # create the tables
  agency_table = table_def_from_entity( Agency, metadata )
  routes_table = table_def_from_entity( Route, metadata )
  trips_table = table_def_from_entity( Trip, metadata )
  stop_times_table = table_def_from_entity( StopTime, metadata )
  calendar_table = table_def_from_entity( ServicePeriod, metadata )
  calendar_dates_table = table_def_from_entity( ServiceException, metadata )
  fare_attributes_table = table_def_from_entity( Fare, metadata )
  fare_rules_table = table_def_from_entity( FareRule, metadata )
  stops_table = table_def_from_entity( Stop, metadata )
  shapes_table = table_def_from_entity( ShapePoint, metadata )
  frequencies_table = table_def_from_entity( Frequency, metadata )
  transfers_table = table_def_from_entity( Transfer, metadata )

  # map the tables
  sqlalchemy.orm.mapper(Agency, agency_table) 
  sqlalchemy.orm.mapper(Route, routes_table, properties={'agency':relationship(Agency,backref="routes")})
  sqlalchemy.orm.mapper(Stop, stops_table)
  sqlalchemy.orm.mapper(Trip, trips_table, properties={'route':relationship(Route, backref="trips"),
					'service_period':relationship(ServicePeriod, backref="trips"),
					'stop_times':relationship(StopTime, order_by="stop_sequence"),
					'shape_points':relationship(ShapePoint, order_by="shape_pt_sequence")})
  sqlalchemy.orm.mapper(StopTime, stop_times_table, properties={'trip':relationship(Trip),
                                                                'stop':relationship(Stop, backref="stop_times")})
  sqlalchemy.orm.mapper(ServicePeriod, calendar_table)
  sqlalchemy.orm.mapper(ServiceException, calendar_dates_table, properties={'service_period':relationship(ServicePeriod,backref="exceptions")})
  sqlalchemy.orm.mapper(Fare, fare_attributes_table)
  sqlalchemy.orm.mapper(FareRule, fare_rules_table, properties={'fare':relationship(Fare,backref="rules"),
                                                                'route':relationship(Route,backref="fare_rules")})
  sqlalchemy.orm.mapper(ShapePoint, shapes_table)
  sqlalchemy.orm.mapper(Frequency, frequencies_table, properties={'trip':relationship(Trip,backref="frequencies")})
  sqlalchemy.orm.mapper(Transfer, transfers_table, properties={"from_stop":relationship(Stop,primaryjoin=transfers_table.c.from_stop_id==stops_table.c.stop_id,backref="transfers_away"),
                                                "to_stop":relationship(Stop,primaryjoin=transfers_table.c.to_stop_id==stops_table.c.stop_id,backref="transfers_from")})

