# Experimental: generate networks from JSON Schema data based
# on super-weird annotations.
import six
import logging
import networkx as nx
from networkx.readwrite import json_graph
from collections import Mapping

from jsonmapping import SchemaVisitor

log = logging.getLogger(__name__)

GRAPH_NODE = 'node'
GRAPH_EDGE = 'edge'


class Network(object):
    """ This operator will consume a set of JSON schema-defined entities
    and attempt to generate a network based on their linkages. For this,
    special annotations are added to the network, which describe the
    'graph' role of the given schema (i.e. 'node', or 'edge'). """
    # FIXME: this assets all entities have an ID

    def __init__(self, resolver):
        self.resolver = resolver
        self.graph = nx.MultiGraph()
        self.edge_ids = set()

    def _get_visitor(self, entity, schema=None):
        if schema is None:
            schema = entity.get('$schema')
        if isinstance(schema, six.string_types):
            schema = {'$ref': schema}
        if schema is None:
            raise TypeError('No schema defined for network mapping.')
        return SchemaVisitor(schema, self.resolver)

    def _simple_object(self, entity, visitor):
        data = {}
        for prop in visitor.properties:
            if prop.is_value and prop.name in entity:
                data[prop.name] = entity.get(prop.name)
        return data

    def _get_nodes(self, entity, visitor, parent=None):
        source_id = parent
        for prop in visitor.properties:
            data = entity.get(prop.name)
            if data is None or prop.graph != GRAPH_NODE:
                continue
            data_id = data.get('id')
            if data_id is None:
                continue

            if not self.graph.has_node(data_id):
                attrs = self._simple_object(data, prop)
                self.graph.add_node(data_id, attr_dict=attrs)

            if source_id is None:
                source_id = data_id

            elif source_id != data_id:
                return max(source_id, data_id), min(source_id, data_id)

        log.warning("Dangling edge: %r; source: %s", entity, source_id)

    def _add_entity(self, entity, visitor, parent=None):
        if visitor.is_object and isinstance(entity, Mapping):
            attrs = self._simple_object(entity, visitor)
            entity_id = entity.get('id')

            if visitor.graph == GRAPH_NODE:
                if not self.graph.has_node(entity_id):
                    self.graph.add_node(entity_id, attr_dict=attrs)

            if visitor.graph == GRAPH_EDGE:
                edge = self._get_nodes(entity, visitor, parent=parent)
                if edge is not None and entity_id not in self.edge_ids:
                    self.graph.add_edge(edge[0], edge[1], attr_dict=attrs)

            # Recurse down the entity
            for prop in visitor.properties:
                self._add_entity(entity.get(prop.name), prop,
                                 parent=entity_id)

        elif visitor.is_array and entity is not None:
            for child in entity:
                self._add_entity(child, visitor.items, parent=parent)

    def add(self, entity, schema=None):
        visitor = self._get_visitor(entity, schema=schema)
        self._add_entity(entity, visitor)

    def to_dict(self):
        return json_graph.node_link_data(self.graph)

    def __repr__(self):
        return '<JSONNetwork()>'
