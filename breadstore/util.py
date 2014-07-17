"""breadStore API utilities library."""

# Standard modules
import re


def case_transform_python(name):
  """Converts a camelCase name to a lower_with_under name."""
  def converter(match):
    return '_' + match.group(1).lower()
  return re.sub('([A-Z])', converter, name)


def case_transform_json(name):
  """Converts a lower_with_under name to camelCase."""
  def converter(match):
    return match.group(1).upper()
  return re.sub('(?:_([a-z]))', converter, name)


def dict_keys_python(mapping):
  """Reformats a dictionary, JSON naming scheme to Python naming scheme."""
  return mapping_visitor(mapping, case_transform_python)


def dict_keys_json(mapping):
  """Reformats a dictionary, Python naming scheme to JSON naming scheme."""
  return mapping_visitor(mapping, case_transform_json)


def mapping_visitor(mapping, key_func):
  """Returns a copy of the mapping after applying key_func to all keys."""
  transformed = {}
  for key, item in mapping.iteritems():
    if isinstance(item, dict):
      item = mapping_visitor(item, key_func)
    transformed[key_func(key)] = item
  return transformed
