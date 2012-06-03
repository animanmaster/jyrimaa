
class DataBag(object):
    def __init__(self, **kwargs):
        for attribute, value in kwargs.iteritems():
            self.__dict__[attribute] = value

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return None

    __getitem__ = __getattr__
    __setitem__ = object.__setattr__

    def __str__(self):
    	return str(self.__dict__)
