import sqlalchemy
import sqlalchemy.orm
from entity import *

class Schedule:
    """Represents a full GTFS data set."""
    
    def __init__(self, db_filename):
        self.db_filename = db_filename
        self.engine = sqlalchemy.create_engine('sqlite:///%s' % self.db_filename, 
                                               echo=False)
        Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = Session()

    @property
    def agencies(self):
        return self.session.query(Agency).all()

    @property
    def stops(self):
        return self.session.query(Stop).all()

    @property
    def routes(self):
        return self.session.query(Route).all()

    @property
    def services(self):
        return self.session.query(Service).all()

    @property
    def service_exceptions(self):
        return self.session.query(ServiceException).all()

    @property
    def trips(self):
        return self.session.query(Trip).all()

    @property
    def stop_times(self):
        return self.session.query(StopTime).all()

    @property
    def fares(self):
        return self.session.query(Fare).all()
            
    @property
    def fare_rules(self):
        return self.session.query(FareRule).all()
                
    @property
    def shape_points(self):
        return self.session.query(ShapePoint).all()
                    
    @property
    def frequencies(self):
        return self.session.query(Frequency).all()
        
    @property
    def transfers(self):
        return self.session.query(Transfer).all()
    
    @property
    def feed_info(self):
        return self.session.query(FeedInfo).all()

    def create_tables(self, metadata):
        metadata.create_all(self.engine) 
