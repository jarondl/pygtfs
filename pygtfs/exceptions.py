class PygtfsException(Exception):
    """ A Base class for all pygtfs exceptions """
    pass

class PygtfsValidationError(PygtfsException, ValueError):
    """ Validation error, e.g. int not in range """
    pass

class PygtfsConversionError(PygtfsException):
    """ Failed conversion, e.g. float(value) failed """
    pass
