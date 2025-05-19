from rdflib import Graph, URIRef, Literal, Namespace, RDF
from typing import Any, Type, List

class RDFMapper:
    def __init__(self):
        self._entities = {}

    def rdf_entity(self, rdf_type_uri: str):
        def wrapper(cls):
            cls._rdf_type_uri = URIRef(rdf_type_uri)
            cls._rdf_properties = {}
            self._entities[cls.__name__] = cls
            return cls
        return wrapper

    def rdf_property(self, predicate_uri: str):
        def decorator(func):
            attr_name = func.__name__

            def getter(self):
                return getattr(self, f"_{attr_name}")

            def setter(self, value):
                setattr(self, f"_{attr_name}", value)

            getter._rdf_predicate = URIRef(predicate_uri)
            getter._is_rdf_property = True
            getter._is_relationship = False

            return property(getter, setter)

        return decorator

    def rdf_one_to_one(self, predicate_uri: str, target_class: Type):
        def decorator(func):
            attr_name = func.__name__

           
            def getter(self):
                return getattr(self, f"_{attr_name}")

            def setter(self, value):
                setattr(self, f"_{attr_name}", value)
                

            getter._rdf_predicate = URIRef(predicate_uri)
            getter._is_rdf_property = True
            getter._is_relationship = True
            getter._relationship_type = 'one_to_one'
            getter._target_class = target_class
            return property(getter, setter)

        return decorator

    def rdf_one_to_many(self, predicate_uri: str, target_class: Type):
        def decorator(func):
            attr_name = func.__name__
           
            def getter(self):
                return getattr(self, f"_{attr_name}")

            def setter(self, value):
                setattr(self, f"_{attr_name}", value)

            getter._rdf_predicate = URIRef(predicate_uri)
            getter._is_rdf_property = True
            getter._is_relationship = True
            getter._relationship_type = 'one_to_many'
            getter._target_class = target_class
            return property(getter, setter)

        return decorator

    def to_rdf(self, obj: Any, base_uri: str = None) -> Graph:
        graph = Graph()
        subject = URIRef(obj.uri if hasattr(obj, 'uri') else base_uri)

        graph.add((subject, RDF.type, obj._rdf_type_uri))

        for attr in dir(obj):
            val = getattr(obj, attr)
            prop = getattr(type(obj), attr, None)
            if hasattr(prop, 'fget') and getattr(prop.fget, '_is_rdf_property', False):
                pred = prop.fget._rdf_predicate
                if getattr(prop.fget, '_is_relationship', False):
                    if prop.fget._relationship_type == 'one_to_one' and val:
                        graph.add((subject, pred, URIRef(val.uri)))
                        graph += self.to_rdf(val)
                    elif prop.fget._relationship_type == 'one_to_many' and isinstance(val, list):
                        for item in val:
                            graph.add((subject, pred, URIRef(item.uri)))
                            graph += self.to_rdf(item)
                else:
                    graph.add((subject, pred, Literal(val)))

        return graph

    def from_rdf(self, graph: Graph, cls: Type, subject_uri: str) -> Any:
        subject = URIRef(subject_uri)
        instance = cls.__new__(cls)
        instance.uri = subject

        for attr in dir(cls):
            prop = getattr(cls, attr, None)
            if hasattr(prop, 'fget') and getattr(prop.fget, '_is_rdf_property', False):
                pred = prop.fget._rdf_predicate
                if getattr(prop.fget, '_is_relationship', False):
                    target_cls = prop.fget._target_class()
                    if prop.fget._relationship_type == 'one_to_one':
                        obj_ref = graph.value(subject, pred)
                        if obj_ref:
                            setattr(instance, attr, self.from_rdf(graph, target_cls, str(obj_ref)))
                    elif prop.fget._relationship_type == 'one_to_many':
                        objs = []
                        for obj_ref in graph.objects(subject, pred):
                            objs.append(self.from_rdf(graph, target_cls, str(obj_ref)))
                        setattr(instance, attr, objs)
                else:
                    val = graph.value(subject, pred)
                    setattr(instance, attr, str(val) if val else None)

        return instance
