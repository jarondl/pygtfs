import map_entities
import sqlalchemy

from unmapped_entities import *

metadata = sqlalchemy.MetaData()
map_entities.create_and_map_tables(metadata)
