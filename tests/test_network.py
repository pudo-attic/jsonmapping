from unittest import TestCase
from nose.tools import raises
from pprint import pprint  # noqa

from jsonmapping.network import Network
from .util import resolver, fixture_uri, fixture_file, csv_mapper


class NetworkTestCase(TestCase):

    def setUp(self):
        super(NetworkTestCase, self).setUp()
        self.mapping, uri = fixture_uri('everypol/mapping.json')
        resolver.store[uri] = self.mapping
        self.csvobj = fixture_file('everypol/term-26.csv')

    @raises(TypeError)
    def test_require_schema(self):
        network = Network(resolver)
        network.add({})

    def test_sa_term26_mapping(self):
        network = Network(resolver)
        for obj in csv_mapper(self.csvobj, self.mapping, resolver=resolver):
            # pprint(obj)
            network.add(obj)

        d3_data = network.to_dict()
        assert 'nodes' in d3_data, d3_data.keys()
        assert 'links' in d3_data, d3_data.keys()
        assert len(d3_data['links']), d3_data['links']

        # assert False
