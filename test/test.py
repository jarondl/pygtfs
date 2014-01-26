from pygtfs import overwrite_feed
from pygtfs import Schedule

import unittest

class TestSchedule(unittest.TestCase):
  def setUp(self):
    self.schedule = Schedule(":memory:")
    overwrite_feed(self.schedule, "test/data/sample-feed.zip" )

  def test_routes( self ):
    self.assertEqual( self.schedule.routes[0].route_id, "AB" )

  def test_service_periods( self ):
    self.assertEqual( [sp.service_id for sp in self.schedule.service_periods],
                      ["WE","WD"] )
    self.assertEqual( type( self.schedule.service_periods[0].monday ),
                      Boolean )

  def test_stops( self ):
    self.assertEqual([st.stop_id for st in self.schedule.stops],
                     [u'FUR_CREEK_RES', u'BEATTY_AIRPORT', u'BULLFROG',
                      u'STAGECOACH', u'NADAV', u'NANAA', u'DADAN', u'EMSI',
                      u'AMV'])

  def test_route_trips( self ):
    self.assertEqual( [tr.trip_id for tr in self.schedule.routes[0].trips],
      [u'AB1', u'AB2'] )

  def test_trip_stop_times( self ):
    self.assertEqual( [(st.arrival_time.val if st.arrival_time else None,
                        st.departure_time.val if st.departure_time else None) for st in self.schedule.routes[0].trips[0].stop_times],
                      [(370, 370), (None, None), (380, 390), (None, None), (405, 405)] )

  def test_service_period_trips( self ):
    self.assertEqual( [tr.trip_id for tr in self.schedule.service_periods[0].trips],
      [u'AWE1'] )

  def test_stop_stop_times( self ):
    self.assertEqual( [(st.arrival_time.val,st.departure_time.val) for st in self.schedule.stops[0].stop_times],
      [(370, 370), (370, 370)] )

  def test_agencies( self ):
    self.assertEqual( [ag.agency_id for ag in self.schedule.agencies],
      [u'DTA'] )

  def test_agency_routes( self ):
    self.assertEqual( [rt.route_id for rt in self.schedule.agencies[0].routes],
      [] )

if __name__=='__main__':
  unittest.main()
