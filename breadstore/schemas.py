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


class Customer(colander.MappingSchema):
  """Schema for a customer, creation and/or updates."""
  klantcode = colander.SchemaNode(
      colander.String(),
      missing=None,
      validator=colander.Length(min=8, max=8))
  voorletters = colander.SchemaNode(
      colander.String(),
      missing='',
      validator=colander.Length(max=16))
  tussenvoegsel = colander.SchemaNode(
      colander.String(),
      missing='',
      validator=colander.Length(max=16))
  achternaam = colander.SchemaNode(
      colander.String(),
      validator=colander.Length(max=32))
  geslacht = colander.SchemaNode(
      colander.String(),
      validator=colander.OneOf(['onbekend', 'man', 'vrouw']))
  geboorte_datum = colander.SchemaNode(
      colander.Date(),
      missing=None)
  email_adres = colander.SchemaNode(
      colander.String(),
      missing=None,
      validator=colander.All(colander.Email(), colander.Length(max=64)))
  adres_straat = colander.SchemaNode(
      colander.String(),
      validator=colander.Length(max=64))
  adres_postcode = colander.SchemaNode(
      colander.String(),
      validator=colander.Length(min=6, max=6))
  adres_plaats = colander.SchemaNode(
      colander.String(),
      validator=colander.Length(max=32))


class Login(colander.MappingSchema):
  """Schema for logging in, requires a login name and password."""
  login = colander.SchemaNode(colander.String())
  password = colander.SchemaNode(colander.String())


class Subscription(colander.MappingSchema):
  """Schema to create or update an existing susbcription.

  Whether or not a certain attribute may be updated depends on the current state
  of the subscription. The start date may not be altered, unless the first
  package has not been collection yet. The number of packages may not be reduced
  below the level of currently handed out packages.
  """
  datum_start = colander.SchemaNode(colander.Date())
  uitgifte_cyclus_id = colander.SchemaNode(colander.Integer())
  opmerking = colander.SchemaNode(colander.String(), missing='')
  pakket_aantal = colander.SchemaNode(colander.Integer())
