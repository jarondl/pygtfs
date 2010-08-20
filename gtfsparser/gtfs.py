import sqlalchemy.types as types
import re

class GTFSForeignKey(str):
  pass

class GTFSBoolean(object):
  def __init__(self, val):
    val = int(val)
    if val not in (0,1):
      raise ValueError( "Boolean values must be '0' or '1'" )
    self.val = val

  def __int__(self):
    return self.val

  def __repr__(self):
    return repr(self.val)


class GTFSTime(object):

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

def make_gtfs_foreign_key_class(cls):
  class ret(GTFSForeignKey):
    _cls = cls
  return ret

class GTFSField(object):
  def __init__(self, fieldtype):
    self.fieldtype = fieldtype

class GTFSEntity(object):
  def __init__(self):
    pass

  @classmethod
  def fields(cls):
    print cls.__dict__

    for name,attr in cls.__dict__.items():
      if isinstance( attr, GTFSField ):
        yield( name, attr )

  def __init__(self, **kwargs):
    for attrname, attrtype in self.FIELDS:
      if attrname in kwargs:
        attrvaluestr = kwargs[attrname]
	if attrvaluestr == '':
	  attrvalue = None
	else:
	  attrvalue = attrtype( attrvaluestr )

        setattr( self, attrname, attrvalue )
