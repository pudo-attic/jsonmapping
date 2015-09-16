import six
from hashlib import sha1

import normality


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
    """ Merge all the strings. Put space between them. """
    return [' '.join([six.text_type(v) for v in values])]


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
