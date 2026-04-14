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

from sqlalchemy.orm import Query


class TestSchedule(unittest.TestCase):
    def setUp(self):
        self.schedule = Schedule(":memory:")
        data_location = os.path.join(os.path.dirname(__file__),
                                     "data", "feed_routes_without_agency_id")
        overwrite_feed(self.schedule, data_location)

    def test_routes(self):
        self.assertEqual(self.schedule.routes[0].route_id, "MB")
    
    def test_routes_agency_id(self):
        """
        Test that despite the agency_id is not defined in routes.txt, due to is not mandatory, 
        it has recognized this case and complete this field on routes table
        """
        self.assertEqual(self.schedule.routes[0].agency_id, "Metro Bilbao")

    


if __name__ == '__main__':
    unittest.main()
