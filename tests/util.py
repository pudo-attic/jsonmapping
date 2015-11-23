import os
import json
import urllib
import unicodecsv

from jsonschema import RefResolver  # noqa

fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
BASE_URI = 'http://www.popoloproject.com/schemas'


def fixture_file(path):
    file_name = os.path.join(fixtures_dir, path)
    return open(file_name, 'rb')


def fixture_uri(path):
    base = os.path.join(fixtures_dir, path)
    base_uri = 'file://' + urllib.pathname2url(base)
    with open(base, 'rb') as fh:
        return json.load(fh), base_uri


def create_resolver():
    resolver = RefResolver(BASE_URI, BASE_URI)
    schemas = os.path.join(fixtures_dir, 'schemas')
    for fn in os.listdir(schemas):
        path = os.path.join(schemas, fn)
        with open(path, 'rb') as fh:
            data = json.load(fh)
            resolver.store[data.get('id')] = data
    return resolver


resolver = create_resolver()


def csv_mapper(fileobj, mapping, resolver=None, scope=None):
    """ Given a CSV file object (fh), parse the file as a unicode CSV document,
    iterate over all rows of the data and map them to a JSON schema using the
    mapping instructions in ``mapping``. """
    from jsonmapping import Mapper
    reader = unicodecsv.DictReader(fileobj)
    for row in Mapper.apply_iter(reader, mapping, resolver=resolver,
                                 scope=scope):
        yield row
