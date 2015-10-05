from unittest import TestCase
import unicodecsv

from jsonmapping import Mapper

from .util import resolver, fixture_uri, fixture_file


def csv_mapper(fileobj, mapping, resolver=None, scope=None):
    """ Given a CSV file object (fh), parse the file as a unicode CSV document,
    iterate over all rows of the data and map them to a JSON schema using the
    mapping instructions in ``mapping``. """
    reader = unicodecsv.DictReader(fileobj)
    for row in Mapper.apply_iter(reader, mapping, resolver=resolver,
                                 scope=scope):
        yield row


class MappingTestCase(TestCase):

    def setUp(self):
        super(MappingTestCase, self).setUp()

    def test_basic_countries_mapping(self):
        mapping, uri = fixture_uri('countries/mapping.json')
        resolver.store[uri] = mapping
        csvobj = fixture_file('countries/countries.csv')
        mapped = list(csv_mapper(csvobj, mapping, resolver=resolver,
                                 scope=uri))
        assert len(mapped) == 255, len(mapped)
        row0 = mapped[0]
        assert isinstance(row0, dict), row0

    def test_sa_term26_mapping(self):
        mapping, uri = fixture_uri('everypol/mapping.json')
        resolver.store[uri] = mapping
        csvobj = fixture_file('everypol/term-26.csv')
        mapped = list(csv_mapper(csvobj, mapping, resolver=resolver))
        assert len(mapped) == 397, len(mapped)
        row0 = mapped[0]
        assert isinstance(row0, dict), row0
        print row0
        assert row0['id'].startswith('popolo:person:'), row0
