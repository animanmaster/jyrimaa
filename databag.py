
class DataBag:
    def __init__(self, **kwargs):
        for attribute, value in kwargs.iteritems():
            self.__dict__[attribute] = value

    def __getattr__(self, attr):
        if attr in self.__dict__.keys():
            return self.__dict__[attr]
        else:
            return None
