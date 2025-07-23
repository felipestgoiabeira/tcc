# baseline_rdflib.py
from rdflib import Graph, Namespace, URIRef, Literal, RDF
from rdflib.namespace import FOAF

EX = Namespace("http://example.org/")

g = Graph()
g.bind("ex", EX)
g.bind("foaf", FOAF)

# cria URIs
pessoa_uri = EX["pessoa/1"]
endereco_uri = EX["endereco/1"]

# adiciona tipo
g.add((pessoa_uri, RDF.type, EX.Pessoa))
g.add((endereco_uri, RDF.type, EX.Endereco))

# propriedades literais
g.add((pessoa_uri, FOAF.name, Literal("Ana Maria")))
g.add((endereco_uri, EX.logradouro, Literal("Rua Central, 123")))

# relação pessoa → endereço
g.add((pessoa_uri, EX.moradia, endereco_uri))

# serializa arquivo

g.serialize(format="turtle", destination="baseline.ttl")
print("baseline.ttl gerado!")