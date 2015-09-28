""" These are utility functions used by the OCCRP datamapper to generate a
matching ElasticSearch schema, given a JSON Schema descriptor. """
from jsonmapping.visitor import SchemaVisitor


def generate_schema_mapping(resolver, schema_uri):
    """ Try and recursively iterate a JSON schema and to generate an ES mapping
    that encasulates it. """
    visitor = SchemaVisitor({'$ref': schema_uri}, resolver)
    return _generate_schema_mapping(visitor, set())


def _generate_schema_mapping(visitor, path):
    if visitor.is_object:
        mapping = {'type': 'nested', 'properties': {}}
        if not visitor.parent:
            mapping['type'] = 'object'
        if visitor.path in path:
            return mapping
        sub_path = path.union([visitor.path])
        for prop in visitor.properties:
            prop_mapping = _generate_schema_mapping(prop, sub_path)
            mapping['properties'][prop.name] = prop_mapping
        return mapping
    elif visitor.is_array:
        for vis in visitor.items:
            return _generate_schema_mapping(vis, path)
    else:
        type_name = 'string'
        if 'number' in visitor.types:
            type_name = 'float'
        if 'integer' in visitor.types:
            type_name = 'long'
        if 'boolean' in visitor.types:
            type_name = 'boolean'
        return {'type': type_name, 'index': 'not_analyzed'}
