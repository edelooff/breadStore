"""Security model for breadStore."""

# Third-party modules
from sqlalchemy import orm

# Application modules
from . import models


def group_finder(user_id, request):
  """Retrieves the user and returns the list of principals for this user

  In addition to providing the principals, the user object is stored on the
  request, allowing easy access to it in views.
  """
  user = request.db.query(models.Medewerker).options(
      orm.joinedload('rol.permissies', innerjoin=True)).get(user_id)
  if user:
    request.user = user
    principals = ['user:%s' % user.id, 'group:%s' % user.rol.naam]
    principals.extend('priv:%s' % priv.naam for priv in user.rol.permissies)
    return principals
