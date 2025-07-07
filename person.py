from rdflib import Namespace
from rdf_mapper.rdf_mapper import RDFMapper
# Inicializa o mapper
rdf_mapper = RDFMapper()
EX = Namespace("http://example.org/")

@rdf_mapper.rdf_entity(EX.Person)
class Person:
    def __init__(self, uri, name=None, address=None, phones=None):
        self.uri = uri
        self._name = name
        self._address = address
        self._phones = phones or []

    @rdf_mapper.rdf_property(EX.name)
    def name(self): pass

    @rdf_mapper.rdf_one_to_one(EX.address, target_class=lambda: Address)
    def address(self): pass

    @rdf_mapper.rdf_one_to_many(EX.phone, target_class=lambda: Phone)
    def phones(self): pass


@rdf_mapper.rdf_entity(EX.Address)
class Address:
    def __init__(self, uri, street=None):
        self.uri = uri
        self._street = street

    @rdf_mapper.rdf_property(EX.street)
    def street(self): pass
    


@rdf_mapper.rdf_entity(EX.Phone)
class Phone:
    def __init__(self, uri, number=None):
        self.uri = uri
        self.number = number

    @rdf_mapper.rdf_property(EX.number)
    def number(self): pass


# Instanciando objetos
addr = Address("http://example.org/address/1", "123 Main St")
phones = [
    Phone("http://example.org/phone/1", "1234-5678"),
    Phone("http://example.org/phone/2", "8765-4321")
]
person = Person("http://example.org/person/1", "João", addr, phones)

# Serializa para RDF
g = rdf_mapper.to_rdf(person)
print(g.serialize(format="xml"))

# Desserializa do RDF
p2 = rdf_mapper.from_rdf(g, Person, "http://example.org/person/1")
print(p2.name, p2.address.street, [ph.number for ph in p2.phones])
