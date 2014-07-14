"""Web API for breadStore."""

# Third-party modules
from pyramid import authentication
from pyramid import authorization
from pyramid import renderers
from pyramid.config import Configurator
import simplejson
import sqlalchemy
import sqlalchemy.orm
import zope.sqlalchemy

# Application modules
from . import security


def request_scoped_session(request):
  """Returns a database session."""
  session = request.registry.dbmaker()

  def close(_request):
    session.close()

  request.add_finished_callback(close)
  return session


def main(global_config, **settings):
  """ This function returns a Pyramid WSGI application."""
  config = Configurator(settings=settings)
  config.add_renderer('json', renderers.JSON(serializer=simplejson.dumps))
  config.add_request_method(request_scoped_session, 'db', reify=True)
  config.set_authentication_policy(
      authentication.AuthTktAuthenticationPolicy(
          config.registry.settings['authentication_secret'],
          callback=security.group_finder,
          cookie_name='bs_auth',
          hashalg='sha512',
          http_only=True,
          reissue_time=3600,
          timeout=24 * 3600,
          wild_domain=True))
  config.set_authorization_policy(authorization.ACLAuthorizationPolicy())

  config.registry.dbmaker = sqlalchemy.orm.sessionmaker(
      bind=sqlalchemy.engine_from_config(settings),
      extension=zope.sqlalchemy.ZopeTransactionExtension())
  config.scan()
  return config.make_wsgi_app()
