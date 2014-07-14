"""Web API for breadStore."""

# Third-party modules
from pyramid import renderers
from pyramid.config import Configurator
import simplejson
import sqlalchemy
import sqlalchemy.orm
import zope.sqlalchemy


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
  config.registry.dbmaker = sqlalchemy.orm.sessionmaker(
      bind=sqlalchemy.engine_from_config(settings),
      extension=zope.sqlalchemy.ZopeTransactionExtension())
  config.scan()
  return config.make_wsgi_app()
