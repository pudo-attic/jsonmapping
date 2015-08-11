import six
from hashlib import sha1

import normality
import typecast


def extract_value(mapping, bind, data):
    """ Given a mapping and JSON schema spec, extract a value from ``data``
    and apply certain transformations to normalize the value. """
    columns = mapping.get('columns', [mapping.get('column')])
    values = [data.get(c) for c in columns]

    for transform in mapping.get('transforms', []):
        # any added transforms must also be added to the schema.
        values = list(TRANSFORMS[transform](mapping, bind, values))

    value = values[0] if len(values) else None
    empty = value is None or \
        (isinstance(value, six.string_types) and not len(value.strip()))

    if empty:
        value = mapping.get('default') or bind.schema.get('default')
    return empty, convert_value(bind, value)


def convert_value(bind, value):
    """ Type casting. """
    # TODO: currently, this will only generate the values supported by JSON
    # schema, but dates and datetimes should be supported as well. Need to
    # find a good work-around, e.g. based on ``format``.
    types = bind.types + [bind.schema.get('format')]
    for type_name in ('date-time', 'date', 'decimal', 'integer', 'boolean',
                      'number', 'string'):
        if type_name in types:
            try:
                return typecast.cast(type_name, value)
            except typecast.ConverterError:
                pass
    return value


def coalesce(mapping, bind, values):
    """ Given a list of values, return the first non-null value. """
    for value in values:
        if value is not None:
            return [value]
    return []


def slugify(mapping, bind, values):
    """ Transform all values into URL-capable slugs. """
    return [normality.slugify(v) for v in values]


def join(mapping, bind, values):
    """ Merge all the strings. No space between them? """
    return [''.join([six.text_type(v) for v in values])]


def str_func(name):
    """ Apply functions like upper(), lower() and strip(). """
    def func(mapping, bind, values):
        for v in values:
            if isinstance(v, six.string_types):
                v = getattr(v, name)()
            yield v
    return func


def hash(mapping, bind, values):
    """ Generate a sha1 for each of the given values. """
    for v in values:
        if not isinstance(v, six.string_types):
            v = six.text_type(v)
        v = v.encode('utf-8')
        yield sha1(v).hexdigest()


TRANSFORMS = {
    'coalesce': coalesce,
    'slugify': slugify,
    'join': join,
    'upper': str_func('upper'),
    'lower': str_func('lower'),
    'strip': str_func('strip'),
    'hash': hash
}
