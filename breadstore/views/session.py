"""breadStore API views - session module."""

# Standard modules
import operator

# Third-party modules
from pyramid import httpexceptions as exc
from pyramid import security
from pyramid.view import view_config
from pyramid.view import view_defaults

# Application modules
from .. import models


@view_defaults(context='..resources.Session', renderer='json')
class SessionApi(object):
  def __init__(self, request):
    self.request = request

  @view_config(request_method='GET', permission='get')
  def get(self):
    """Return an object describing the permissions of the user."""
    get_name = operator.attrgetter('naam')
    return {'permissies': map(get_name, self.request.user.rol.permissies)}

  @view_config(request_method='POST', permission='login')
  def login(self):
    """Handles session creation, or user login.

    Returns 401 Unautorized if either the login or password is incorrect.
    Returns 303 See Other to retrieve the principals if they are correct.
    """
    user = self.request.db.query(models.Medewerker).filter(
        models.Medewerker.login == self.request.json_body['login']).first()
    if user and user.verify_password(self.request.json_body['password']):
      auth_ticket = security.remember(self.request, user.id)
      return exc.HTTPSeeOther('/session', headers=auth_ticket)
    return exc.HTTPUnauthorized(json={'error': 'bad credentials'})

  @view_config(request_method='DELETE', permission='logout')
  def logout(self):
    """Logs out the user, has no return."""
    return exc.HTTPNoContent(headers=security.forget(self.request))
