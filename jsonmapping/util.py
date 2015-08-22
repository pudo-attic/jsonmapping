import os
import json

from jsonschema import Draft4Validator


def validate_mapping(mapping):
    """ Validate a mapping configuration file against the relevant schema. """
    file_path = os.path.join(os.path.dirname(__file__),
                             'schemas', 'mapping.json')
    with open(file_path, 'rb') as fh:
        validator = Draft4Validator(json.load(fh))
        validator.validate(mapping)
    return mapping


class RefScoped(object):
    """ Objects which have a JSON schema-style scope. """

    def __init__(self, resolver, scoped, scope=None, parent=None, name=None):
        self.resolver = resolver
        self._scoped = scoped
        self._scope = scope or ''
        self.name = name
        self.parent = parent

    @property
    def id(self):
        return self._scoped.get('id')

    @property
    def path(self):
        if self.id is not None:
            return self.id
        if self.parent:
            path = self.parent.path
            if self.name:
                if '#' not in path:
                    return path + '#/' + self.name
                else:
                    return path + '/' + self.name
            return path

    @property
    def scope(self):
        if self.id:
            return self.id
        if self.parent:
            return self.parent.scope
        return self._scope
