import unittest
from rdflib import Namespace
from src.rdf_mapper import RDFMapper
from src.rdf_repository import RDFRepository
from rdflib import Graph

EX = Namespace("http://example.org/")
rdf_mapper = RDFMapper()

@rdf_mapper.rdf_entity(EX.Person)
class Person:
    def __init__(self, uri, name=None):
        self.uri = uri
        self._name = name

    @rdf_mapper.rdf_property(EX.name)
    def name(self): pass


class TestRDFRepository(unittest.TestCase):
    def setUp(self):
        self.person = Person("http://example.org/person/1", "João")
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

if __name__ == "__main__":
    unittest.main()
