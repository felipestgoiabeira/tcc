from rdflib import Graph, URIRef, Literal, Namespace, RDF, XSD
from typing import Any, Type, List
import datetime

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
    

    def _python_to_literal(self, value):
        """Converte valor Python em Literal com datatype adequado"""
        if isinstance(value, bool):
            return Literal(value, datatype=XSD.boolean)
        elif isinstance(value, int):
            return Literal(value, datatype=XSD.integer)
        elif isinstance(value, float):
            return Literal(value, datatype=XSD.double)
        elif isinstance(value, datetime.date):
            return Literal(value.isoformat(), datatype=XSD.date)
        elif isinstance(value, datetime.datetime):
            return Literal(value.isoformat(), datatype=XSD.dateTime)
        else:
            return Literal(value)

    def _literal_to_python(self, literal: Literal):
        """Converte Literal RDF para valor Python, baseado no datatype"""
        if literal is None:
            return None
        dt = literal.datatype
        val = str(literal)
        if dt == XSD.boolean:
            return val.lower() in ("true", "1")
        elif dt == XSD.integer:
            return int(val)
        elif dt == XSD.double:
            return float(val)
        elif dt == XSD.date:
            return datetime.date.fromisoformat(val)
        elif dt == XSD.dateTime:
            return datetime.datetime.fromisoformat(val)
        else:
            return val

    def to_rdf(self, obj: Any, base_uri: str = None, visited=None) -> Graph:
        if visited is None:
            visited = set()

        graph = Graph()
        subject = URIRef(obj.uri if hasattr(obj, 'uri') else base_uri)

        if subject in visited:
            # Já serializado antes, só cria o link para evitar loop
            graph.add((subject, RDF.type, obj._rdf_type_uri))
            return graph

        visited.add(subject)
        graph.add((subject, RDF.type, obj._rdf_type_uri))

        for attr in dir(obj):
            val = getattr(obj, attr)
            prop = getattr(type(obj), attr, None)
            if hasattr(prop, 'fget') and getattr(prop.fget, '_is_rdf_property', False):
                pred = prop.fget._rdf_predicate
                if getattr(prop.fget, '_is_relationship', False):
                    if prop.fget._relationship_type == 'one_to_one' and val:
                        graph.add((subject, pred, URIRef(val.uri)))
                        graph += self.to_rdf(val, visited=visited)
                    elif prop.fget._relationship_type == 'one_to_many' and isinstance(val, list):
                        for item in val:
                            graph.add((subject, pred, URIRef(item.uri)))
                            graph += self.to_rdf(item, visited=visited)
                else:
                    if val is not None:
                        graph.add((subject, pred, self._python_to_literal(val)))

        return graph

    def from_rdf(self, graph: Graph, cls: Type, subject_uri: str, visited=None) -> Any:
        if visited is None:
            visited = {}

        subject = URIRef(subject_uri)

        if subject in visited:
            return visited[subject]

        instance = cls.__new__(cls)
        instance.uri = subject
        visited[subject] = instance

        for attr in dir(cls):
            prop = getattr(cls, attr, None)
            if hasattr(prop, 'fget') and getattr(prop.fget, '_is_rdf_property', False):
                pred = prop.fget._rdf_predicate
                if getattr(prop.fget, '_is_relationship', False):
                    target_cls = prop.fget._target_class()
                    if prop.fget._relationship_type == 'one_to_one':
                        obj_ref = graph.value(subject, pred)
                        if obj_ref:
                            setattr(instance, attr, self.from_rdf(graph, target_cls, str(obj_ref), visited))
                    elif prop.fget._relationship_type == 'one_to_many':
                        objs = []
                        for obj_ref in graph.objects(subject, pred):
                            objs.append(self.from_rdf(graph, target_cls, str(obj_ref), visited))
                        setattr(instance, attr, objs)
                else:
                    val = graph.value(subject, pred)
                    setattr(instance, attr, self._literal_to_python(val))

        return instance
    
    def to_rdf_many(self, objs: list) -> Graph:
        graph = Graph()
        visited = set()
        for obj in objs:
            graph += self.to_rdf(obj, visited=visited)
        return graph
