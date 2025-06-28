# 🧠 RDFMapper

Um mini-framework inspirado no JPA, mas para dados RDF em Python.

## ✨ Funcionalidades

- 🔧 Mapeamento de classes Python para entidades RDF
- 🔗 Relacionamentos RDF: `one_to_one`, `one_to_many`
- 🔍 Consultas dinâmicas estilo JPA: `find_by_*`, `find_by_*_like`
- 📊 Paginação (`limit`, `offset`) e contagem (`count_by_*`)
- 🧠 Suporte à serialização e desserialização com prevenção de circularidade
- ✅ Testes robustos com grafos grandes e circulares

---

## 💪 Instalação

Instale em modo desenvolvimento:

```bash
pip install -e .
```

Requisitos:
- Python 3.8+
- [`rdflib`](https://github.com/RDFLib/rdflib)

---

## 🥚 Testes

Execute os testes com:

```bash
PYTHONPATH=. python tests/rdf_repository_test.py
```

Os testes cobrem:

- Mapeamento e relacionamento entre entidades
- Paginação e contagem
- Grafos RDF com circularidade
- Performance com milhares de registros

---

## 🛆 Exemplo de uso

```python
from rdflib import Namespace
from rdf_mapper import RDFMapper, RDFRepository

EX = Namespace("http://example.org/")
rdf_mapper = RDFMapper()

@rdf_mapper.rdf_entity(EX.Person)
class Person:
    def __init__(self, uri, name=None):
        self.uri = uri
        self._name = name

    @rdf_mapper.rdf_property(EX.name)
    def name(self): pass

p = Person("http://example.org/person/1", "João")
g = rdf_mapper.to_rdf(p)
repo = RDFRepository(rdf_mapper, g, Person)

results = repo.find_by_name(name="João")
print(results[0].name)
```

---

## 📄 Licença

MIT License. Livre para uso e modificação.

---

## ✨ Contribua

Pull Requests e melhorias são bem-vindos. Sugestões de features como ordenação, filtros avançados e suporte a OWL são encorajadas!
