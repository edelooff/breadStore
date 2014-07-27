"""breadStore API views - subscription module."""

# Third-party modules
from pyramid.view import view_config
from pyramid.view import view_defaults


@view_defaults(context='..resources.Subscription')
class SubscriptionView(object):
  def __init__(self, context, request):
    self.request = request
    self.sub = context.subscription

  @view_config(request_method='GET', permission='view')
  def get(self):
    """Returns the information of a subscription."""
    return {'subscription': self.sub}
