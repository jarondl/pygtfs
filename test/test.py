import datetime

from pygtfs import overwrite_feed
from pygtfs import Schedule

import unittest

class TestSchedule(unittest.TestCase):
  def setUp(self):
    self.schedule = Schedule(":memory:")
    overwrite_feed(self.schedule, "test/data/sample-feed.zip" )

  def test_routes( self ):
    self.assertEqual( self.schedule.routes[0].route_id, "AB" )

  def test_services( self ):
    self.assertEqual( [service.service_id for service in self.schedule.services],
                      ["FULLW","WE"] )

  def test_stops( self ):
    self.assertEqual([st.stop_id for st in self.schedule.stops],
                     [u'FUR_CREEK_RES', u'BEATTY_AIRPORT', u'BULLFROG',
                      u'STAGECOACH', u'NADAV', u'NANAA', u'DADAN', u'EMSI',
                      u'AMV'])

  def test_route_trips( self ):
    self.assertEqual( [tr.trip_id for tr in self.schedule.routes[0].trips],
      [u'AB1', u'AB2'] )

  def test_trip_stop_times( self ):
    self.assertEqual( [(st.arrival_time if st.arrival_time else None,
                        st.departure_time if st.departure_time else None) for st in self.schedule.routes[0].trips[0].stop_times],
                        [(datetime.timedelta(0, 28800), datetime.timedelta(0, 28800)),
                         (datetime.timedelta(0, 29400), datetime.timedelta(0, 29700))])

  def test_service_trips( self ):
    self.assertEqual([tr.trip_id for tr in self.schedule.services[1].trips],
                     [u'AAMV1', u'AAMV2', u'AAMV3', u'AAMV4'])

  def test_stop_stop_times( self ):
    self.assertEqual([(st.arrival_time,st.departure_time) for st in self.schedule.stops[0].stop_times],
                     [(datetime.timedelta(0, 33600), datetime.timedelta(0, 33600)),
                      (datetime.timedelta(0, 39600), datetime.timedelta(0, 39600))])

  def test_agencies( self ):
    self.assertEqual( [ag.agency_id for ag in self.schedule.agencies],
      [u'DTA'] )

  def test_agency_routes( self ):
    self.assertEqual([rt.route_id for rt in self.schedule.agencies[0].routes],
                     [u'AAMV', u'AB', u'BFC', u'CITY', u'STBA'])

if __name__=='__main__':
  unittest.main()
