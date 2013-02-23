import sqlalchemy
import sqlalchemy.orm
from entity import *

class Schedule:
    """Represents a full GTFS data set."""
    
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

    @property
    def agencies(self):
        return self.session.query(Agency).all()
    
    @property
    def agencies_by_id(self):
        return dict(zip([x.agency_id for x in self.agencies], self.agencies))

    @property
    def stops(self):
        return self.session.query(Stop).all()
    
    @property
    def stops_by_id(self):
        return dict(zip([x.stop_id for x in self.stops], self.stops))

    @property
    def routes(self):
        return self.session.query(Route).all()
    
    @property
    def routes_by_id(self):
        return dict(zip([x.route_id for x in self.routes], self.routes))

    @property
    def services(self):
        return self.session.query(Service).all()
    
    @property
    def services_by_id(self):
        return dict(zip([x.service_id for x in self.services], self.services))

    @property
    def service_exceptions(self):
        return self.session.query(ServiceException).all()

    @property
    def trips(self):
        return self.session.query(Trip).all()
    
    @property
    def trips_by_id(self):
        return dict(zip([x.trip_id for x in self.trips], self.trips))

    @property
    def stop_times(self):
        return self.session.query(StopTime).all()

    @property
    def fares(self):
        return self.session.query(Fare).all()
    
    @property
    def fares_by_id(self):
        return dict(zip([x.fare_id for x in self.fares], self.fares))
            
    @property
    def fare_rules(self):
        return self.session.query(FareRule).all()
                
    @property
    def shape_points(self):
        return self.session.query(ShapePoint).all()
        
    @property
    def shape_points_by_id(self):
        return dict(zip([x.shape_id for x in self.shape_points], self.shape_points))
                    
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
