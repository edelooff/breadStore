"""breadStore API views."""

# Standard modules
import operator

# Third-party modules
from pyramid import httpexceptions as exc
from pyramid import security
from pyramid.view import view_config
from pyramid.view import view_defaults

# Application modules
from . import models


@view_config(renderer='json')
def root(request):
  return {'application': 'breadStore'}
