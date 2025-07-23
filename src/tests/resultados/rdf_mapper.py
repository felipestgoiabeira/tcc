from rdflib import Namespace, Literal
from src.rdf_mapper.rdf_mapper import RDFMapper

EX = Namespace("http://example.org/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

rdf_mapper = RDFMapper() 

@rdf_mapper.rdf_entity(EX.Endereco)
class Endereco:
    def __init__(self, uri, logradouro):
        self.uri = uri
        self._logradouro = Literal(logradouro)

    @rdf_mapper.rdf_property(EX.logradouro)
    def logradouro(self): pass

@rdf_mapper.rdf_entity(EX.Pessoa)
class Pessoa:
    def __init__(self, uri, nome, endereco):
        self.uri = uri
        self._nome = Literal(nome)
        self._endereco = endereco

    @rdf_mapper.rdf_property(FOAF.name)
    def nome(self): pass

    @rdf_mapper.rdf_one_to_one(EX.moradia, target_class=lambda: Endereco)
    def endereco(self): pass

# instancia objetos
end = Endereco(EX["endereco/1"], "Rua Central, 123")
pes = Pessoa(EX["pessoa/1"], "Ana Maria", end)

# serializa
g = rdf_mapper.to_rdf(pes)
g.serialize(destination="mapper.ttl", format="turtle")
print("mapper.ttl gerado!")
