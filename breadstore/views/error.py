"""breadStore API views - errors module."""

# Third-party modules
from pyramid import httpexceptions as exc
from pyramid.view import view_config


@view_config(context=exc.HTTPForbidden)
def forbidden_view(request):
  """Handles requests that the client is forbidden from performing."""
  return error_response(request, 'forbidden', code=403)


@view_config(context=exc.HTTPNotFound)
def notfound_view(request):
  """Handles requests for unavailable resources."""
  return error_response(request, 'not found', code=404)


def error_response(request, message, code=400, **kwds):
  """Creates an error response by setting the code and message."""
  kwds.setdefault('error', message)
  request.response.status_int = code
  return kwds
