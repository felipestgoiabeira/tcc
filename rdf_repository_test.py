import unittest
from rdflib import Namespace
from src.rdf_mapper import RDFMapper
from src.rdf_repository import RDFRepository
from rdflib import Graph

EX = Namespace("http://example.org/")
rdf_mapper = RDFMapper()

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
        self._number = number

    @rdf_mapper.rdf_property(EX.number)
    def number(self): pass


class TestRDFRepository(unittest.TestCase):
    def setUp(self):
        address = Address("http://example.org/address/1", "123 Main St")
        phones = [
            Phone("http://example.org/phone/1", "1234-5678"),
            Phone("http://example.org/phone/2", "8765-4321")
        ]
        self.person = Person("http://example.org/person/1", "João", address, phones)
        self.graph = rdf_mapper.to_rdf(self.person)
        self.repo = RDFRepository(rdf_mapper, self.graph, Person)

    def test_find_by_name(self):
        results = self.repo.find_by_name(name="João")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "João")

    def test_find_by_name_like(self):
        results = self.repo.find_by_name_like(name="jo")
        self.assertEqual(len(results), 1)

    def test_count_by_name(self):
        count = self.repo.count_by_name(name="João")
        self.assertEqual(count, 1)

    def test_limit_offset(self):
        p2 = Person("http://example.org/person/2", "João")
        self.graph += rdf_mapper.to_rdf(p2)
        results = self.repo.find_by_name(name="João", limit=1)
        self.assertEqual(len(results), 1)
        results_offset = self.repo.find_by_name(name="João", limit=1, offset=1)
        self.assertEqual(len(results_offset), 1)

    def test_relationships(self):
        person_from_graph = self.repo.find_by_name(name="João")[0]
        self.assertIsNotNone(person_from_graph.address)
        self.assertEqual(person_from_graph.address.street, "123 Main St")
        self.assertEqual(len(person_from_graph.phones), 2)
        self.assertIn("1234-5678", [p.number for p in person_from_graph.phones])

if __name__ == "__main__":
    unittest.main()
