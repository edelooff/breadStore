"""breadStore API views."""

# Third-party modules
from pyramid.view import view_config


@view_config(context='..resources.Root', renderer='json')
def root(request):
  return {'application': 'breadStore'}
