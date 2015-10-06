from jsonmapping.visitor import SchemaVisitor
from jsonmapping.value import extract_value
from jsonmapping.util import validate_mapping


class Mapper(object):
    """ Given a JSON-specified mapping, this class will recursively transform
    a flat data structure (e.g. a CSV file or database table) into a nested
    JSON structure as specified by the JSON schema associated with the given
    mapping. """

    def __init__(self, mapping, resolver, visitor=None, scope=None):
        self.mapping = mapping.copy()
        if '$ref' in self.mapping:
            with resolver.in_scope(scope):
                uri, data = resolver.resolve(self.mapping.pop('$ref'))
                self.mapping.update(data)
        if visitor is None:
            schema = self.mapping.get('schema')
            visitor = SchemaVisitor(schema, resolver, scope=scope)
        self.visitor = visitor
        if self.visitor.parent is None:
            validate_mapping(self.mapping) is not None

    @property
    def optional(self):
        """ If optional, the object will be skipped if no values exist in
        source data to fill it up. """
        return self.mapping.get('optional', False)

    @property
    def children(self):
        if not hasattr(self, '_children'):
            if self.visitor.is_array:
                self._children = Mapper(self.mapping, self.visitor.resolver,
                                        visitor=self.visitor.items)
            elif self.visitor.is_object:
                self._children = []
                for name, mappings in self.mapping.get('mapping', {}).items():
                    if hasattr(mappings, 'items'):
                        mappings = [mappings]
                    for mapping in mappings:
                        for prop in self.visitor.properties:
                            if prop.match(name):
                                mapper = Mapper(mapping, self.visitor.resolver,
                                                visitor=prop)
                                self._children.append(mapper)
            else:
                self._children = None
        return self._children

    def apply(self, data):
        """ Apply the given mapping to ``data``, recursively. The return type
        is a tuple of a boolean and the resulting data element. The boolean
        indicates whether any values were mapped in the child nodes of the
        mapping. It is used to skip optional branches of the object graph. """
        if self.visitor.is_object:
            obj = {}
            if self.visitor.parent is None:
                obj['$schema'] = self.visitor.path
            obj_empty = True
            for child in self.children:
                empty, value = child.apply(data)
                if empty and child.optional:
                    continue
                obj_empty = False if not empty else obj_empty

                if child.visitor.name in obj and child.visitor.is_array:
                    obj[child.visitor.name].extend(value)
                else:
                    obj[child.visitor.name] = value
            return obj_empty, obj

        elif self.visitor.is_array:
            empty, value = self.children.apply(data)
            return empty, [value]

        elif self.visitor.is_value:
            return extract_value(self.mapping, self.visitor, data)

    @classmethod
    def apply_iter(cls, rows, mapping, resolver, scope=None):
        """ Given an iterable ``rows`` that yield data records, and a
        ``mapping`` which is to be applied to them, return a tuple of
        ``data`` (the generated object graph) and ``err``, a validation
        exception if the resulting data did not match the expected schema. """
        mapper = cls(mapping, resolver, scope=scope)
        for row in rows:
            _, data = mapper.apply(row)
            yield data
