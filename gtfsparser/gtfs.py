
class GTFSForeignKey(str):
  pass

class GTFSBoolean(int):
  def __init__(self, val):
    val = int(val)
    if val not in (0,1):
      raise ValueError( "Boolean values must be '0' or '1'" )
    int.__init__(self,val)


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
