from copy import deepcopy


class SchemaVisitor(object):
    """ A schema visitor traverses a JSON schema with associated data and
    allows the user to perform any transformations on the data that they
    wish. """

    def __init__(self, schema, resolver, name=None, parent=None, scope=None):
        self.cls = type(self)
        self.name = name
        self.parent = parent
        self.resolver = resolver

        if '$ref' in schema:
            with resolver.in_scope(scope):
                uri, schema_ = resolver.resolve(schema.get('$ref'))
                schema = deepcopy(schema)
                schema.pop('$ref', None)
                schema.update(schema_)

        self.schema = schema
        self.id = schema.get('id')

        self.types = schema.get('type', 'object')
        if not isinstance(self.types, list):
            self.types = [self.types]
        self.is_object = 'object' in self.types
        self.is_array = 'array' in self.types
        self.is_value = not (self.is_object or self.is_array)

        if self.id:
            self.scope = self.id
        elif self.parent:
            self.scope = self.parent.scope
        else:
            self.scope = scope

    def match(self, name):
        return self.name == name

    @property
    def title(self):
        return self.schema.get('title', self.name)

    @property
    def plural(self):
        return self.schema.get('plural', self.title)

    @property
    def inline(self):
        if self.is_value:
            return True
        return self.schema.get('inline', False)

    @property
    def sort_index(self):
        return self.schema.get('sortIndex', 0)

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
    def inherited(self):
        if not hasattr(self, '_inherited'):
            self._inherited = []
            for inheritance_rule in ('anyOf', 'allOf', 'oneOf'):
                for schema in self.schema.get(inheritance_rule, []):
                    visitor = self.cls(schema, self.resolver, name=self.name,
                                       parent=self.parent)
                    self._inherited.append(visitor)
        return self._inherited

    @property
    def properties(self):
        if not self.is_object:
            return []

        if not hasattr(self, '_properties'):
            self._properties = []
            for visitor in self.inherited:
                for prop in visitor.properties:
                    self._properties.append(prop)

            for name, schema in self.schema.get('properties', {}).items():
                self._properties.append(self.cls(schema, self.resolver,
                                                 name=name, parent=self))

            self._properties = list(sorted(self._properties,
                                           key=lambda v: v.sort_index,
                                           reverse=True))
            # TODO: patternProperties - probably can't support them fully.
        return self._properties

    @property
    def items(self):
        if not self.is_array:
            return
        if not hasattr(self, '_items'):
            schema = self.schema.get('items')
            self._items = self.cls(schema, self.resolver, name=self.name,
                                   parent=self)
        return self._items

    def __repr__(self):
        return '<SchemaVisitor(%r,%r)>' % (self.name, self.title)
