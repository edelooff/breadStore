"""breadStore API views - customer module."""

# Third-party modules
from pyramid.view import view_config
from pyramid.view import view_defaults

# Application modules
from .. import models
from .. import schemas
from .. import util


@view_defaults(context='..resources.CustomerCollection')
class CustomerCollectionView(object):
  """Defines the customer collection API."""
  def __init__(self, request):
    self.request = request

  @view_config(request_method='GET', permission='view')
  def list(self):
    """Returns a list of customers in the system."""
    return {'klanten': self.request.db.query(models.Klant).all()}

  @view_config(request_method='POST', permission='create')
  def create(self):
    """Creates a new customer and returns a single object response."""
    schema = load_customer_schema(self.request)
    customer = models.Klant(**schema)
    self.request.db.add(customer)
    self.request.db.flush()
    return {'klant': customer}


@view_defaults(context='..resources.Customer')
class CustomerView(object):
  """Defines the single customer API."""
  def __init__(self, context, request):
    self.request = request
    self.customer = context.customer

  @view_config(request_method='GET', permission='view')
  def get(self):
    """Returns the information of a customer."""
    return {'klant': self.customer}

  @view_config(request_method='PUT', permission='update')
  def update(self):
    """Updates an existing customer."""
    schema = load_customer_schema(self.request)
    for key, value in schema.iteritems():
      setattr(self.customer, key, value)
    return {'klant': self.customer}

  @view_config(name='abonnementen', request_method='GET', permission='view')
  def list_subscriptions(self):
    return {'abonnementen': self.customer.abonnementen}


def load_customer_schema(request):
  """Loads the customer schema and sets a customer code if it's None."""
  schema = schemas.load(schemas.Customer, request)
  if not schema['klantcode']:
    schema['klantcode'] = util.timebased_customer_code()
  return schema
