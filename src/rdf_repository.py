import re
from rdflib import Namespace, Literal

class RDFRepository:
    def __init__(self, rdf_mapper, graph, entity_class):
        self.mapper = rdf_mapper
        self.graph = graph
        self.entity_class = entity_class

    def __getattr__(self, name):
        match = re.match(r'^find_by_(.+)$', name)
        if match:
            fields = match.group(1).split('_and_')
            def finder(**kwargs):
                return self._find_by(fields, kwargs)
            return finder
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

    def _find_by(self, fields, values):
        cls = self.entity_class
        subject_var = "?s"
        conditions = []

        for field in fields:
            if field not in values:
                raise ValueError(f"Missing value for field '{field}'")
            
            value = values[field]
            prop = getattr(cls, field, None)
            if not prop:
                raise AttributeError(f"Field '{field}' not found in class '{cls.__name__}'")

            pred = prop.fget._rdf_predicate
            if getattr(prop.fget, '_is_relationship', False):
                # Relacionamento: usamos URI
                conditions.append(f"{subject_var} <{pred}> <{value}> .")
            else:
                # Propriedade simples: usamos Literal
                conditions.append(f'{subject_var} <{pred}> "{value}" .')

        rdf_type = cls._rdf_type_uri
        where_clause = "\n".join(conditions)

        query = f"""
        SELECT ?s WHERE {{
            {subject_var} a <{rdf_type}> .
            {where_clause}
        }}
        """

        results = []
        for row in self.graph.query(query):
            obj = self.mapper.from_rdf(self.graph, cls, str(row.s))
            results.append(obj)

        return results
