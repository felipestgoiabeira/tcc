from rdflib import Namespace, Literal
from src.rdf_mapper.rdf_mapper import RDFMapper
from rdflib import Graph
from pyshacl import validate

EX = Namespace("http://example.org/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

rdf_mapper = RDFMapper() 


@rdf_mapper.rdf_entity(EX.Person)
class Person:
    def __init__(self, uri, nome, idade: int, email):
        self.uri = uri
        self._nome = Literal(nome)
        self._idade = Literal(idade)
        self._email = Literal(email)

    @rdf_mapper.rdf_property(FOAF.name, minCount=1)
    def nome(self): pass

    @rdf_mapper.rdf_property(FOAF.age)
    def idade(self): pass

    @rdf_mapper.rdf_property(FOAF.mbox)
    def email(self): pass


person = Person(
    uri="https://example.org/persons/1",
    nome="Felipe",
    idade=25,
    email="joao@example.com"
)

# Serialize para RDF
rdf_mapper = RDFMapper()
person_graph: Graph = rdf_mapper.to_rdf(person)

# Carrega o shape
shape_graph = Graph()
shape_graph.parse("src/tests/shacl/person-shape.ttl", format="turtle")

# Validação
conforms, report_graph, report_text = rdf_mapper.validate(person_graph, entity_class=Person)
# Resultado
print("Validação passou:", conforms)
print("Relatório:")
print(report_text)


print(rdf_mapper.to_shacl(Person).serialize(format="turtle"))

conforms, report_graph, report_text = rdf_mapper.validate(person_graph, entity_class=Person)

# Resultado
print("Validação passou:", conforms)
print("Relatório:")
print(report_text)