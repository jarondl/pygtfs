import re
from datetime import date, datetime

class ForeignKey(str):
  pass

class Boolean(object):
  def __init__(self, val):
    val = int(val)
    if val not in (0,1):
      raise ValueError( "Boolean values must be '0' or '1'" )
    self.val = val

  def __int__(self):
    return self.val

  def __repr__(self):
    return repr(self.val)

class Time(object):

  def __init__(self, timerepr):
    if isinstance( timerepr, int ):
      self.val = timerepr
    elif isinstance( timerepr, basestring ):
      self.val = self._time_to_seconds_since_midnight( timerepr )
    else:
      raise Exception( "timerepr must be str or int, found %s"%type(timerepr) )
    
  def _time_to_seconds_since_midnight(self, time_string):
    """Convert HHH:MM:SS into seconds since midnight.

    For example "01:02:03" returns 3723. The leading zero of the hours may be
    omitted. HH may be more than 23 if the time is on the following day."""
    m = re.match(r'(\d{1,3}):([0-5]\d):([0-5]\d)$', time_string)
    # ignored: matching for leap seconds
    if not m:
      raise ValueError( 'Bad HH:MM:SS "%s"' % time_string )
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
  
  def _format_seconds_since_midnight(self, s):
    """Formats an int number of seconds past midnight into a string
    as "HH:MM:SS"."""
    return "%02d:%02d:%02d" % (s / 3600, (s / 60) % 60, s % 60)

  def __repr__(self):
    return "<Time %s>"%self._format_seconds_since_midnight(self.val)

  def __int__(self):
    return self.val

  def __eq__(self,other):
    return self.val==other.val

  def __sub__(self,other):
    return self.val-other.val 

class Date(object):
  def __init__(self, daterepr):
    if isinstance( daterepr, int ):
      self.val = date.fromordinal( daterepr )
    elif isinstance( daterepr, date ):
      self.val = daterepr
    elif isinstance( daterepr, basestring ):
      self.val = self._date_string_to_date_object( daterepr )
    else:
      raise Exception( "daterepr must be basetring, int, or date, found %s"%type(daterepr) )
      
  def _date_string_to_date_object(self, date_string):
    """Return a date object for a string "YYYYMMDD"."""
    # If this becomes a bottleneck date objects could be cached
    return date(int(date_string[0:4]), int(date_string[4:6]),
                         int(date_string[6:8]))

def make_gtfs_foreign_key_class(cls):
  class ret(ForeignKey):
    _cls = cls
  return ret

