from gtfsparser.loader import load
from gtfsparser import metadata
from gtfsparser.schedule import Schedule

import unittest

class TestSchedule(unittest.TestCase):
  def setUp(self):
    self.schedule = load( metadata, "test/data/sample-feed.zip" )

  def test_routes( self ):
    self.assertEqual( self.schedule.routes[0].route_id, "A" )

  def test_service_periods( self ):
    self.assertEqual( [sp.service_id for sp in self.schedule.service_periods],
                      ["WE","WD"] )

  def test_stops( self ):
    self.assertEqual( [st.stop_id for st in self.schedule.stops],
      [u'S1', u'S2', u'S3', u'S4', u'S5', u'S6', u'S7', u'S8'] )

  def test_route_trips( self ):
    self.assertEqual( [tr.trip_id for tr in self.schedule.routes[0].trips],
      [u'AWE1', u'AWD1'] )

  def test_trip_stop_times( self ):
    self.assertEqual( [(st.arrival_time,st.departure_time) for st in self.schedule.routes[0].trips[0].stop_times],
      [(u'0:06:10', u'0:06:10'), (None, None), (u'0:06:20', u'0:06:30'), (None, None), (u'0:06:45', u'0:06:45')] )

  def test_service_period_trips( self ):
    self.assertEqual( [tr.trip_id for tr in self.schedule.service_periods[0].trips],
      [u'AWE1'] )

  def test_stop_stop_times( self ):
    self.assertEqual( [(st.arrival_time,st.departure_time) for st in self.schedule.stops[0].stop_times],
      [(u'0:06:10', u'0:06:10'), (u'0:06:10', u'0:06:10')] )

  def test_agencies( self ):
    self.assertEqual( [ag.agency_id for ag in self.schedule.agencies],
      [u'FunBus'] )

  def test_agency_routes( self ):
    self.assertEqual( [rt.route_id for rt in self.schedule.agencies[0].routes],
      [] )

if __name__=='__main__':
  unittest.main()
