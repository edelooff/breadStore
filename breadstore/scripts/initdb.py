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
  if options.get('recreate') == 'true':
    models.Base.metadata.drop_all(engine)
  models.Base.metadata.create_all(engine)
