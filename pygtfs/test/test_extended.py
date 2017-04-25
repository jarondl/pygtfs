# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import os.path
# use unittest2 for Python2.6 compatibility. 
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pygtfs import overwrite_feed
from pygtfs import Schedule


class TestExtendedSchedule(unittest.TestCase):
    def setUp(self):
        self.schedule = Schedule(":memory:")
        data_location = os.path.join(os.path.dirname(__file__),
                                     "data", "sample_feed_extended")
        overwrite_feed(self.schedule, data_location)

    def test_routes(self):
        self.assertEqual(self.schedule.routes[0].route_id, "AB")


    def test_agency_routes(self):
        self.assertEqual([rt.route_id for rt in self.schedule.agencies[0].routes],
                         ['AAMV', 'AB', 'BFC', 'CITY', 'EXT', 'STBA'])


if __name__ == '__main__':
    unittest.main()
