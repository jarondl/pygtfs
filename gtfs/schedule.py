import sqlalchemy
from entity import *

class Schedule:
  def __init__( self, db_filename ):
    self.db_filename = db_filename

    self.engine = sqlalchemy.create_engine('sqlite:///%s'%self.db_filename, echo=False)
    Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
    self.session = Session()

  @property
  def routes(self):
    return self.session.query(Route).all()

  @property
  def agencies(self):
    return self.session.query(Agency).all()

  @property
  def service_periods(self):
    return self.session.query(ServicePeriod).all()

  @property
  def stops(self):
    return self.session.query(Stop).all()

  def create_tables( self ):
    metadata.create_all(self.engine) 
