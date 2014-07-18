"""breadStore API schemas."""

# Third-party modules
import colander

# Application modules
from . import resources
from . import util


def load(schema, request, content_type='application/json'):
  """Deserializes the values according to the given Colander schema.

  Field names are changed from JavaScript to Python notation where required.
  """
  if request.content_type != content_type:
    raise resources.ApiError('content_type must be %r' % content_type, code=415)
  try:
    values = request.json_body
  except ValueError:
    raise resources.ApiError('Cannot deserialize request body, invalid JSON.')
  return schema().deserialize(util.dict_keys_python(values))


class Login(colander.MappingSchema):
  """Schema for logging in, requires a login name and password."""
  login = colander.SchemaNode(colander.String())
  password = colander.SchemaNode(colander.String())
