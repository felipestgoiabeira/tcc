import re

class RDFRepository:
    def __init__(self, rdf_mapper, graph, entity_class):
        self.mapper = rdf_mapper
        self.graph = graph
        self.entity_class = entity_class

    def __getattr__(self, name):
        if name.startswith("count_by_"):
            fields = name[len("count_by_"):].split("_and_")
            def counter(**kwargs):
                return self._count_by(fields, kwargs)
            return counter

        match = re.match(r'^find_by_(.+)$', name)
        if match:
            fields = match.group(1).split('_and_')
            def finder(**kwargs):
                limit = kwargs.pop("limit", None)
                offset = kwargs.pop("offset", None)
                return self._find_by(fields, kwargs, like="_like" in name, limit=limit, offset=offset)
            return finder

        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

    def _find_by(self, fields, values, like=False, limit=None, offset=None):
        cls = self.entity_class
        subject_var = "?s"
        conditions = []

        for field in fields:
            field_name = field.replace('_like', '')
            if field_name not in values:
                raise ValueError(f"Missing value for field '{field_name}'")
            value = values[field_name]
            prop = getattr(cls, field_name)
            pred = prop.fget._rdf_predicate

            if getattr(prop.fget, '_is_relationship', False):
                conditions.append(f"{subject_var} <{pred}> <{value}> .")
            else:
                value_var = f"?v_{field_name}"
                conditions.append(f"{subject_var} <{pred}> {value_var} .")
                if '_like' in field:
                    conditions.append(f'FILTER regex({value_var}, "{value}", "i")')
                else:
                    conditions.append(f'FILTER ({value_var} = "{value}")')

        rdf_type = cls._rdf_type_uri
        where_clause = "\n".join(conditions)
        query = f"""
        SELECT ?s WHERE {{
            {subject_var} a <{rdf_type}> .
            {where_clause}
        }}
        """
        if limit is not None:
            query += f"\nLIMIT {limit}"
        if offset is not None:
            query += f"\nOFFSET {offset}"

        return [
            self.mapper.from_rdf(self.graph, cls, str(row.s))
            for row in self.graph.query(query)
        ]

    def _count_by(self, fields, values):
        cls = self.entity_class
        subject_var = "?s"
        conditions = []

        for field in fields:
            if field not in values:
                raise ValueError(f"Missing value for field '{field}'")
            value = values[field]
            prop = getattr(cls, field)
            pred = prop.fget._rdf_predicate
            if getattr(prop.fget, '_is_relationship', False):
                conditions.append(f"{subject_var} <{pred}> <{value}> .")
            else:
                conditions.append(f'{subject_var} <{pred}> "{value}" .')

        rdf_type = cls._rdf_type_uri
        where_clause = "\n".join(conditions)
        query = f"""
        SELECT (COUNT(?s) as ?count) WHERE {{
            {subject_var} a <{rdf_type}> .
            {where_clause}
        }}
        """
        result = self.graph.query(query)
        for row in result:
            return int(row[0].toPython())
        return 0

    
    def group_by_count(self, cls, field: str, order: str = "DESC"):
            graph = self.graph
            class_uri = cls._rdf_type_uri

            prop = getattr(cls, field, None)
            if not hasattr(prop, 'fget') or not hasattr(prop.fget, '_rdf_predicate'):
                raise ValueError(f"'{field}' is not a valid rdf_property")

            predicate = prop.fget._rdf_predicate
            order = order.strip().upper()
            if order not in ("ASC", "DESC"):
                raise ValueError("order must be 'ASC' or 'DESC'")

            query = f"""
                SELECT ?{field} (COUNT(?s) AS ?count)
                WHERE {{
                ?s a <{class_uri}> ;
                    <{predicate}> ?{field} .
                }}
                GROUP BY ?{field}
                ORDER BY {order}(?count)
            """

            qres = graph.query(query)
            return [{field: str(row[0]), "count": int(row[1])} for row in qres]