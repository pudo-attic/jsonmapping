import six
import typecast

from jsonmapping.transforms import TRANSFORMS


def extract_value(mapping, bind, data):
    """ Given a mapping and JSON schema spec, extract a value from ``data``
    and apply certain transformations to normalize the value. """
    columns = mapping.get('columns', [mapping.get('column')])
    values = [data.get(c) for c in columns]

    for transform in mapping.get('transforms', []):
        # any added transforms must also be added to the schema.
        values = list(TRANSFORMS[transform](mapping, bind, values))

    format_str = mapping.get('format')
    value = values[0] if len(values) else None
    if not is_empty(format_str):
        value = format_str % tuple('' if v is None else v for v in values)

    empty = is_empty(value)
    if empty:
        value = mapping.get('default') or bind.schema.get('default')
    return empty, convert_value(bind, value)


def get_type(bind):
    """ Detect the ideal type for the data, either using the explicit type
    definition or the format (for date, date-time, not supported by JSON). """
    types = bind.types + [bind.schema.get('format')]
    for type_name in ('date-time', 'date', 'decimal', 'integer', 'boolean',
                      'number', 'string'):
        if type_name in types:
            return type_name
    return 'string'


def convert_value(bind, value):
    """ Type casting. """
    type_name = get_type(bind)
    try:
        return typecast.cast(type_name, value)
    except typecast.ConverterError:
        return value


def flatten_value(mapping, bind):
    """ Return a value to its original column. """
    type_name = get_type(bind)
    value = bind.data
    try:
        value = typecast.stringify(type_name, value)
    except typecast.ConverterError:
        pass
    name = mapping.get('columns', [mapping.get('column')])[0]
    name = mapping.get('dump', name)
    return name, value


def is_empty(value):
    if value is None:
        return True
    if isinstance(value, six.string_types):
        return len(value.strip()) < 1
    return False
