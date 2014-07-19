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
    return {'klanten': self.request.db.query(models.Klant).all()}


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
