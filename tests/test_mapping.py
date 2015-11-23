from unittest import TestCase

from .util import resolver, fixture_uri, fixture_file, csv_mapper


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
