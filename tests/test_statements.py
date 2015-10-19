from unittest import TestCase

from jsonmapping import StatementsVisitor

from .util import resolver, fixture_uri


def load_maker(stmts):
    def _load(subject):
        return [(p, o, 'foo') for (s, p, o, t) in stmts if s == subject]
    return _load


class StatementsTestCase(TestCase):

    def setUp(self):
        self.mapping, self.uri = fixture_uri('everypol/mapping.json')
        self.schema_uri = 'http://www.popoloproject.com/schemas/person.json#'
        self.schema = {'$ref': self.schema_uri}
        resolver.store[self.uri] = self.mapping
        super(StatementsTestCase, self).setUp()

    def test_basic_statement_conversion(self):
        sv = StatementsVisitor(self.schema, resolver)
        data = {
            'name': 'The Count'
        }
        stmts = list(sv.triplify(data))
        assert len(stmts) == 2, len(stmts)
        subj = [a for a, _, _, _ in stmts]
        assert len(set(subj)) == 1, subj
        assert subj[0].startswith('urn:uuid'), subj

    def test_subject_properties(self):
        sv = StatementsVisitor(self.schema, resolver)
        data = {
            'id': 'the-count',
            'name': 'The Count'
        }
        stmts = list(sv.triplify(data))
        assert len(stmts) == 3, len(stmts)
        subj = [a for a, _, _, _ in stmts]
        assert len(set(subj)) == 1, subj
        assert subj[0] == 'the-count', subj

    def test_nested_object(self):
        sv = StatementsVisitor(self.schema, resolver)
        data = {
            'id': 'the-count',
            'name': 'The Count',
            'memberships': [{
                'role': 'Counter',
                'organization': {
                    'name': 'Beans'
                }
            }]
        }
        stmts = list(sv.triplify(data))
        assert len(stmts) == 9, len(stmts)
        subj = [a for a, _, _, _ in stmts]
        assert len(set(subj)) == 3, subj

    def test_reverse_objectify(self):
        sv = StatementsVisitor(self.schema, resolver)
        data = {
            'id': 'the-count',
            'name': 'The Count',
            'memberships': [{
                'role': 'Counter',
                'organization': {
                    'id': 'beans',
                    'name': 'Beans'
                }
            }]
        }
        stmts = list(sv.triplify(data))
        loader = load_maker(stmts)
        obj = sv.objectify(loader, data['id'], depth=4)
        assert obj['id'] == data['id']
        oname = obj['memberships'][0]['organization']['name']
        dname = obj['memberships'][0]['organization']['name']
        assert oname == dname, obj
