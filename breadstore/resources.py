"""Resource tree for breadStore"""


class Root(dict):
  """Root resource factory."""
  def __init__(self, request):
    self.request = request
    self['session'] = Session(self, 'session')


class Session(object):
  """Login session tracker."""
  def __init__(self, parent, name):
    self.__parent__ = parent
    self.__name__ = name

  def __acl__(self):
    yield 'Allow', 'system.Everyone', 'login'
    yield 'Allow', 'system.Authenticated', 'get'
    yield 'Allow', 'system.Authenticated', 'logout'
