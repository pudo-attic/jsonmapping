from jsonschema import Draft4Validator, ValidationError

from jsonmapper.visitor import SchemaVisitor
from jsonmapper.value import extract_value
from jsonmapper.util import validate_mapping, RefScoped


class Mapper(RefScoped):
    """ Given a JSON-specified mapping, this class will recursively transform
    a flat data structure (e.g. a CSV file or database table) into a nested
    JSON structure as specified by the JSON schema associated with the given
    mapping. """

    def __init__(self, mapping, resolver, schema=None, bind=None, parent=None,
                 scope=None, name=None):
        self._mapping = mapping.copy()
        self._schema = schema or {}
        self._bind = bind
        self._validator = None
        self._valid = name is not None
        self._children = None
        super(Mapper, self).__init__(resolver, self._mapping, name=name,
                                     scope=scope, parent=parent)

    @property
    def mapping(self):
        """ Mappings can be given as references only, resolve first. """
        if '$ref' in self._mapping:
            with self.resolver.in_scope(self.scope):
                uri, data = self.resolver.resolve(self._mapping.pop('$ref'))
                self._mapping.update(data)
        if not self._valid:
            self._valid = validate_mapping(self._mapping) is not None
        return self._mapping

    @property
    def optional(self):
        """ If optional, the object will be skipped if no values exist in
        source data to fill it up. """
        return self.mapping.get('optional', False)

    @property
    def validator(self):
        if self._validator is None:
            self._validator = Draft4Validator(self.bind.schema,
                                              resolver=self.resolver)
        return self._validator

    @property
    def bind(self):
        """ The JSON schema spec matching the current level of the mapping. """
        if self._bind is None:
            schema = self.mapping.get('schema', self._schema)
            self._bind = SchemaVisitor(schema, self.resolver,
                                       scope=self.scope)
        return self._bind

    @property
    def children(self):
        if not self.bind.is_object:
            return []
        if self._children is None:
            self._children = []
            for name, mappings in self.mapping.get('mapping', {}).items():
                if hasattr(mappings, 'items'):
                    mappings = [mappings]
                for mapping in mappings:
                    for prop in self.bind.properties:
                        if prop.match(name):
                            mapper = Mapper(mapping, self.resolver,
                                            schema=prop.schema, bind=prop,
                                            parent=self, name=name)
                            self._children.append(mapper)
        return self._children

    def apply(self, data):
        """ Apply the given mapping to ``data``, recursively. The return type
        is a tuple of a boolean and the resulting data element. The boolean
        indicates whether any values were mapped in the child nodes of the
        mapping. It is used to skip optional branches of the object graph. """
        if self.bind.is_object:
            obj, obj_empty = {}, True
            for child in self.children:
                empty, value = child.apply(data)
                if empty and child.optional:
                    continue
                obj_empty = False if not empty else obj_empty

                if child.name in obj and child.bind.is_array:
                    obj[child.name].extend(value)
                else:
                    obj[child.name] = value
            return obj_empty, obj

        elif self.bind.is_array:
            for item in self.bind.items:
                bind = Mapper(self.mapping, self.resolver,
                              schema=item.schema, bind=item,
                              parent=self, name=self.name)
                empty, value = bind.apply(data)
                return empty, [value]

        elif self.bind.is_value:
            return extract_value(self.mapping, self.bind, data)

    @classmethod
    def from_mapping(cls, mapping, resolver, scope=None):
        return cls(mapping, resolver, scope=scope)

    @classmethod
    def from_iter(cls, rows, mapping, resolver, scope=None):
        """ Given an iterable ``rows`` that yield data records, and a
        ``mapping`` which is to be applied to them, return a tuple of
        ``data`` (the generated object graph) and ``err``, a validation
        exception if the resulting data did not match the expected schema. """
        mapper = cls.from_mapping(mapping, resolver, scope=scope)
        for row in rows:
            err = None
            _, data = mapper.apply(row)
            try:
                mapper.validator.validate(data)
            except ValidationError, ve:
                err = ve
            yield data, err
