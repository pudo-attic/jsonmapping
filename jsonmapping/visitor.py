

class SchemaVisitor(object):
    """ A schema visitor traverses a JSON schema with associated data and
    allows the user to perform any transformations on the data that they
    wish. """

    def __init__(self, schema, resolver, data=None, name=None, parent=None,
                 scope=None):
        self.name = name
        self.parent = parent
        self.resolver = resolver

        if '$ref' in schema:
            with resolver.in_scope(scope):
                uri, schema = resolver.resolve(schema.get('$ref'))

        self.schema = schema
        self.id = schema.get('id')
        self.types = schema.get('type', 'object')
        if not isinstance(self.types, list):
            self.types = [self.types]
        self.is_object = 'object' in self.types
        self.is_array = 'array' in self.types
        self.is_value = not (self.is_object or self.is_array)

        self.data = data

        if self.id:
            self.scope = self.id
        elif self.parent:
            self.scope = self.parent.scope
        else:
            self.scope = scope

    def _visitor(self, parent, schema, data, name):
        return type(self)(schema, self.resolver, data=data, name=name,
                          parent=parent)

    def match(self, name):
        return self.name == name

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
    def properties(self):
        # This will have different results depending on whether data is given
        # or not, due to pattern properties.
        if not self.is_object:
            return

        for inheritance_rule in ('anyOf', 'allOf', 'oneOf'):
            for schema in self.schema.get(inheritance_rule, []):
                visitor = self._visitor(self.parent, schema, self.data,
                                        self.name)
                for prop in visitor.properties:
                    yield prop

        for name, schema in self.schema.get('properties', {}).items():
            data = None if self.data is None else self.data.get(name)
            yield self._visitor(self, schema, data, name)

        # TODO: patternProperties

    @property
    def items(self):
        if not self.is_array:
            return
        if self.data is None:
            yield self._visitor(self, self.schema.get('items'), None,
                                self.name)
        else:
            for item in self.data:
                yield self._visitor(self, self.schema.get('items'), item,
                                    self.name)
