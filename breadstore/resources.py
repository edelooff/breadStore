"""Resource tree for breadStore"""

# Third-party modules
from pyramid import security

# Application modules
from . import models


class ApiError(Exception):
  """Generic API exception."""
  def __init__(self, message, code=400, **kwds):
    super(ApiError, self).__init__(message)
    self.mesage = message
    self.code = code
    self.kwds = kwds


class Resource(object):
  """Baseclass for non-Root resources."""
  def __init__(self, parent, name, **kwds):
    self.__parent__ = parent
    self.__name__ = name
    for key, value in kwds.iteritems():
      setattr(self, key, value)


class Root(dict):
  """Root resource factory."""
  __parent__ = None
  __name__ = None

  def __init__(self, request):
    self.request = request
    self['abonnementen'] = SubscriptionCollection(
        self, 'abonnementen', request=request)
    self['klanten'] = CustomerCollection(self, 'klanten', request=request)
    self['session'] = Session(self, 'session')

  def __acl__(self):
    """Basic ACL allows public views and denies everything else."""
    yield 'Allow', 'system.Everyone', 'none'
    yield security.DENY_ALL


class CustomerCollection(Resource):
  """Customer collection API."""
  def __acl__(self):
    yield 'Allow', 'system.Authenticated', 'view'
    yield 'Allow', 'priv:klant.aanmaken', 'create'
    yield security.DENY_ALL

  def __getitem__(self, key):
    """Loads and returns a customer based on its primary key."""
    if key.isdigit():
      customer = self.request.db.query(models.Klant).get(key)
      if customer:
        return Customer(self, key, customer=customer)
    raise KeyError


class Customer(Resource):
  """Singular customer API."""
  def __acl__(self):
    yield 'Allow', 'priv:klant.aanpassen', 'update'
    yield 'Allow', 'priv:klant.verwijderen', 'delete'


class Session(Resource):
  """Login session tracker."""
  def __acl__(self):
    yield 'Allow', 'system.Everyone', 'login'
    yield 'Allow', 'system.Authenticated', 'get'
    yield 'Allow', 'system.Authenticated', 'logout'


class SubscriptionCollection(Resource):
  """Subscription collection exists for traversal purposes only.

  Subscriptions can be listed/created in the context of a Customer only.
  """
  def __getitem__(self, key):
    """Loads and returns a subscription based on its primary key."""
    if key.isdigit():
      subscription = self.request.db.query(models.Abonnement).get(key)
      if subscription:
        return Subscription(self, key, subscription=subscription)
    raise KeyError


class Subscription(Resource):
  """Subscription API for viewing, updating and suspending of subscription."""
  def __acl__(self):
    yield 'Allow', 'system.Authenticated', 'view'
    yield 'Allow', 'priv:abonnement.aanpassen', 'update'
    yield 'Allow', 'priv:abonnement.dieet.beheren', 'manage_diets'
    yield 'Allow', 'priv:abonnement.stoppen', 'stop'
    yield security.DENY_ALL
