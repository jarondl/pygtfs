# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import os.path

from pygtfs import overwrite_feed
from pygtfs import Schedule

import unittest

class TestSchedule(unittest.TestCase):
  def setUp(self):
    self.schedule = Schedule(":memory:")
    data_location = os.path.join(os.path.dirname(__file__),
                                 "data", "sample_feed")
    overwrite_feed(self.schedule, data_location)

  def test_routes( self ):
    self.assertEqual( self.schedule.routes[0].route_id, "AB" )

  def test_services( self ):
    self.assertEqual( [service.service_id for service in self.schedule.services],
                      ["FULLW","WE"] )

  def test_stops( self ):
    self.assertEqual([st.stop_id for st in self.schedule.stops],
                     ['FUR_CREEK_RES', 'BEATTY_AIRPORT', 'BULLFROG',
                      'STAGECOACH', 'NADAV', 'NANAA', 'DADAN', 'EMSI',
                      'AMV'])

  def test_route_trips( self ):
    self.assertEqual( [tr.trip_id for tr in self.schedule.routes[0].trips],
      ['AB1', 'AB2'] )

  def test_trip_stop_times( self ):
    self.assertEqual( [(st.arrival_time if st.arrival_time else None,
                        st.departure_time if st.departure_time else None) for st in self.schedule.routes[0].trips[0].stop_times],
                        [(datetime.timedelta(0, 28800), datetime.timedelta(0, 28800)),
                         (datetime.timedelta(0, 29400), datetime.timedelta(0, 29700))])

  def test_service_trips( self ):
    self.assertEqual([tr.trip_id for tr in self.schedule.services[1].trips],
                     ['AAMV1', 'AAMV2', 'AAMV3', 'AAMV4'])

  def test_stop_stop_times( self ):
    self.assertEqual([(st.arrival_time,st.departure_time) for st in self.schedule.stops[0].stop_times],
                     [(datetime.timedelta(0, 33600), datetime.timedelta(0, 33600)),
                      (datetime.timedelta(0, 39600), datetime.timedelta(0, 39600))])

  def test_stop_translations(self):
    self.assertEqual([(tr.lang,
                      tr.translation) for tr in self.schedule.stops[0].translations],
                      [('HE', 'אתר הנופש ערוץ הכבשן (דמו)'), ('EN', 'Furnace Creek Resort (Demo)')])


  def test_agencies( self ):
    self.assertEqual( [ag.agency_id for ag in self.schedule.agencies],
      ['DTA'] )

  def test_agency_routes( self ):
    self.assertEqual([rt.route_id for rt in self.schedule.agencies[0].routes],
                     ['AAMV', 'AB', 'BFC', 'CITY', 'STBA'])

  def test_trips_bikes_allowed(self):
    for t in self.schedule.trips:
      self.assertIsNone(t.bikes_allowed)
    t = self.schedule.trips[0]
    t.bikes_allowed = 0
    t.bikes_allowed = 1
    t.bikes_allowed = 2
    with self.assertRaises(AssertionError):
      t.bikes_allowed = 3
    with self.assertRaises(AssertionError):
      t.bikes_allowed = -1
    self.assertEqual(t.bikes_allowed, 2)

if __name__=='__main__':
  unittest.main()
