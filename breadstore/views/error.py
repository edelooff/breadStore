"""breadStore API views - errors module."""

# Third-party modules
from pyramid import httpexceptions as exc
from pyramid.view import view_config


@view_config(context='colander.Invalid')
def schema_validation_error(validation_result, request):
  """Handles schema validation errors."""
  return error_response(
      request,
      'schema validation error, details provided in "invalid".',
      invalid=validation_result.asdict())


@view_config(context='..resources.ApiError')
def bad_request_body(err, request):
  """Handles API usage errors."""
  return error_response(request, err.message, code=err.code, **err.kwds)


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
