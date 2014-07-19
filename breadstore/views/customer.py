"""breadStore API views - customer module."""

# Standard modules
import datetime

# Third-party modules
from pyramid.view import view_config
from pyramid.view import view_defaults

# Application modules
from .. import models


@view_defaults(context='..resources.CustomerCollection')
class CustomerCollectionView(object):
  """Defines the customer collection API."""
  def __init__(self, request):
    self.request = request

  @view_config(request_method='GET', permission='view')
  def list(self):
    """Returns a list of customers in the system."""
    return {'klanten': map(record_to_json, self.request.db.query(models.Klant))}


@view_defaults(context='..resources.Customer')
class CustomerView(object):
  """Defines the single customer API."""
  def __init__(self, context, request):
    self.request = request
    self.customer = context.customer

  @view_config(request_method='GET', permission='view')
  def get(self):
    """Returns the information of a customer."""
    return {'klant': record_to_json(self.customer)}


def record_to_json(record):
  """Turns an SQLA record instance into a simple dictionary for JSON usage."""
  def get(attr):
    value = getattr(record, attr)
    if isinstance(value, (datetime.date, datetime.datetime)):
      return value.isoformat()
    return value

  return {attr: get(attr) for attr in vars(record) if not attr.startswith('_')}
