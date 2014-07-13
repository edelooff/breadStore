from pyramid.view import view_config


@view_config(renderer='json')
def root(request):
  return {'application': 'breadStore'}
