"""breadStore API views - subscription module."""

# Third-party modules
from pyramid import httpexceptions as exc
from pyramid.view import view_config
from pyramid.view import view_defaults

# Application modules
from .. import resources
from .. import schemas

@view_defaults(context='..resources.Subscription')
class SubscriptionView(object):
  """Defines the singular customer API."""
  def __init__(self, context, request):
    self.request = request
    self.sub = context.subscription

  @view_config(request_method='GET', permission='view')
  def get(self):
    """Returns the information of a subscription."""
    return {'subscription': self.sub}

  @view_config(request_method='PUT', permission='update')
  def update(self):
    """Updates an existing subscription."""
    schema = schemas.load(schemas.Subscription, self.request)
    for key, value in schema:
      setattr(self.sub, key, value)
    return {'subscription': self.sub}


  @view_config(request_method='DELETE', permission='delete')
  def delete(self):
    """Deletes the subscription, as long as zero packages were handed out."""
    if self.sub.packages_provided():
      raise resources.ApiError(
          'Cannot delete subscription when packages have been handed out.',
          provided_packages=self.sub.packages_provided())
    self.request.db.delete(self.sub)
    return exc.HTTPNoContent()
