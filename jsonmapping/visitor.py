from jsonmapping.util import RefScoped


class SchemaVisitor(RefScoped):
    """ A schema visitor traverses a JSON schema with associated data and
    allows the user to perform any transformations on the data that they
    wish. """

    def __init__(self, schema, resolver, data=None, name=None, parent=None,
                 state=None, scope=None):
        self._schema = schema.copy()
        self.data = data
        self.state = state
        super(SchemaVisitor, self).__init__(resolver, self._schema, name=name,
                                            scope=scope, parent=parent)

    def _visitor(self, parent, schema, data, name):
        return type(self)(schema, self.resolver, data=data, name=name,
                          parent=parent, state=self.state)

    def match(self, name):
        return self.name == name

    @property
    def schema(self):
        if '$ref' in self._schema:
            with self.resolver.in_scope(self.scope):
                uri, data = self.resolver.resolve(self._schema.pop('$ref'))
                self._schema.update(data)
        return self._schema

    @property
    def types(self):
        types = self.schema.get('type', 'object')
        if not isinstance(types, list):
            types = [types]
        return types

    @property
    def is_object(self):
        return 'object' in self.types

    @property
    def is_array(self):
        return 'array' in self.types

    @property
    def is_value(self):
        return not (self.is_object or self.is_array)

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
