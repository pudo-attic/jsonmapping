import re
import six
from hashlib import sha1
from unidecode import unidecode

import normality

COLLAPSE = re.compile(r'\s+')


def coalesce(mapping, bind, values):
    """ Given a list of values, return the first non-null value. """
    for value in values:
        if value is not None:
            return [value]
    return []


def slugify(mapping, bind, values):
    """ Transform all values into URL-capable slugs. """
    return [normality.slugify(v) for v in values]


def latinize(mapping, bind, values):
    """ Transliterate a given string into the latin alphabet. """
    return [unidecode(v) for v in values if v is not None]


def join(mapping, bind, values):
    """ Merge all the strings. Put space between them. """
    return [' '.join([six.text_type(v) for v in values if v is not None])]


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
        if v is None:
            continue
        if not isinstance(v, six.string_types):
            v = six.text_type(v)
        v = v.encode('utf-8')
        yield sha1(v).hexdigest()


def clean(mapping, bind, values):
    """ Perform several types of string cleaning for titles etc.. """
    categories = {'C': ' '}
    for value in values:
        yield normality.normalize(value, lowercase=False, collapse=True,
                                  decompose=False,
                                  replace_categories=categories)


TRANSFORMS = {
    'coalesce': coalesce,
    'slugify': slugify,
    'clean': clean,
    'latinize': latinize,
    'join': join,
    'upper': str_func('upper'),
    'lower': str_func('lower'),
    'strip': str_func('strip'),
    'hash': hash
}
