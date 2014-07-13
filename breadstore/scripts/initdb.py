# Standard modules
import os
import sys

# Third-party modules
from pyramid import paster
from pyramid.scripts import common
import sqlalchemy
import sqlalchemy.orm
import transaction
import zope.sqlalchemy

# Application modules
from .. import models


def usage(argv):
  cmd = os.path.basename(argv[0])
  print('usage: %s <config_uri> [var=value]\n'
        '(example: "%s development.ini")' % (cmd, cmd))
  sys.exit(1)


def main(argv=sys.argv):
  if len(argv) < 2:
    usage(argv)
  config_uri = argv[1]
  options = common.parse_vars(argv[2:])

  paster.setup_logging(config_uri)
  settings = paster.get_appsettings(config_uri, options=options)
  engine = sqlalchemy.engine_from_config(settings, 'sqlalchemy.')
  models.Base.metadata.create_all(engine)
  session = sqlalchemy.orm.sessionmaker(
      bind=engine, extension=zope.sqlalchemy.ZopeTransactionExtension())()
  with transaction.manager:
    obj = models.MyModel(name='one', value=1)
    session.add(obj)
