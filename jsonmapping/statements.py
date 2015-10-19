import uuid
from collections import Mapping
import typecast

from jsonmapping.visitor import SchemaVisitor


TYPE_SCHEMA = '$schema'
TYPE_LINK = 'link'


class StatementsVisitor(SchemaVisitor):
    """ This class has utility functions for transforming JSON schema defined
    objects into a series of RDF-like statements (i.e. subject, predicate,
    object, context) quads. It can be used independently of any specific
    storage backend, including RDF. """

    def get_subject(self, data):
        """ Try to get a unique ID from the object. By default, this will be
        the 'id' field of any given object, or a field specified by the
        'rdfSubject' property. If no other option is available, a UUID will be
        generated. """
        if not isinstance(data, Mapping):
            return None
        subject = self.schema.get('rdfSubject', 'id')
        if data.get(subject):
            return data.get(subject)
        return uuid.uuid4().urn

    @property
    def predicate(self):
        return self.schema.get('rdfName', self.name)

    @property
    def reverse(self):
        """ Reverse links make sense for object to object links where we later
        may want to also query the reverse of the relationship, e.g. when obj1
        is a child of obj2, we want to infer that obj2 is a parent of obj1. """
        name = self.schema.get('rdfReverse')
        if name is not None:
            return name
        if self.parent is not None and self.parent.is_array:
            return self.parent.reverse

    def get_property(self, predicate):
        for prop in self.properties:
            if predicate == prop.name:
                return prop

    def _triplify_object(self, data, parent):
        """ Create bi-directional statements for object relationships. """
        subject = self.get_subject(data)
        if self.path:
            yield (subject, TYPE_SCHEMA, self.path, TYPE_SCHEMA)

        if parent is not None:
            yield (parent, self.predicate, subject, TYPE_LINK)
            if self.reverse is not None:
                yield (subject, self.reverse, parent, TYPE_LINK)

        for prop in self.properties:
            for res in prop.triplify(data.get(prop.name), subject):
                yield res

    def triplify(self, data, parent=None):
        """ Recursively generate statements from the data supplied. """
        if data is None:
            return

        if self.is_object:
            for res in self._triplify_object(data, parent):
                yield res
        elif self.is_array:
            for item in data:
                for res in self.items.triplify(item, parent):
                    yield res
        else:
            # TODO: figure out if I ever want to check for reverse here.
            type_name = typecast.name(data)
            obj = typecast.stringify(type_name, data)
            yield (parent, self.predicate, obj, type_name)

    # Clever Method Names Award, 2014 and two years running
    def objectify(self, load, node, depth=3, path=None):
        """ Given a node ID, return an object the information available about
        this node. This accepts a loader function as it's first argument, which
        is expected to return all tuples of (predicate, object, source) for
        the given subject. """
        if path is None:
            path = set()

        if self.is_object:
            # Support inline objects which don't count towards the depth.
            next_depth = depth
            if not self.schema.get('inline'):
                next_depth = depth - 1

            sub_path = path.union([node])
            obj = {'$schema': self.path, '$sources': []}
            for (p, o, src) in load(node):
                prop = self.get_property(p)
                if prop is None or next_depth <= 0 or o in path:
                    continue

                # This is slightly odd but yields purty objects:
                # if next_depth <= 1 and (prop.is_array or prop.is_object):
                #    continue

                if src not in obj['$sources']:
                    obj['$sources'].append(src)

                value = prop.objectify(load, o, next_depth, sub_path)
                if prop.is_array and prop.name in obj:
                    obj[prop.name].extend(value)
                else:
                    obj[prop.name] = value
            return obj
        elif self.is_array:
            return [self.items.objectify(load, node, depth, path)]
        else:
            return node
