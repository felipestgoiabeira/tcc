import time
import psutil
import os
import matplotlib.pyplot as plt

from rdflib import Namespace, Literal, URIRef, Graph
from src.rdf_mapper.rdf_mapper import RDFMapper
from src.rdf_mapper.rdf_repository import RDFRepository

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

def memory_mb():
    # Retorna uso de memória do processo atual em MB
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def populate_graph(n=10000, target_name="Pessoa 1234"):
    g = Graph()
    for i in range(n):
        pes_uri = URIRef(EX[f"pessoa/{i}"])
        end_uri = URIRef(EX[f"endereco/{i}"])
        nome = f"Pessoa {i}" if i != 1234 else target_name
        g.add((pes_uri, FOAF.name, Literal(nome)))
        g.add((pes_uri, EX.moradia, end_uri))
        g.add((end_uri, EX.logradouro, Literal("Rua Exemplo")))
    return g

def populate_graph_rdfmapper(n=10000, target_name="Pessoa 1234"):
    objs = []
    for i in range(n):
        end = Endereco(EX[f"endereco/{i}"], "Rua Exemplo")
        nome = f"Pessoa {i}" if i != 1234 else target_name
        pes = Pessoa(EX[f"pessoa/{i}"], nome, end)
        objs.append(pes)
    g = rdf_mapper.to_rdf_many(objs)
    return g

def benchmark_rdflib_query(g, target_name="Pessoa 1234"):
    sparql = f"""
    SELECT ?pessoa WHERE {{
        ?pessoa <{FOAF.name}> "{target_name}" .
    }}
    """
    start = time.perf_counter()
    results = list(g.query(sparql))
    duration = time.perf_counter() - start
    return duration, results

def benchmark_rdfmapper_query(g, target_name="Pessoa 1234"):
    repo = RDFRepository(rdf_mapper, g, Pessoa)
    start = time.perf_counter()
    results = repo.find_by_nome(nome=target_name)
    duration = time.perf_counter() - start
    return duration, results

if __name__ == "__main__":
    VOLUMES = [1000, 10000, 50000, 100000]
    dados = {
        "Volume": [],
        "Tempo_rdf_mapper": [],
        "Tempo_rdflib": [],
        "Memoria_rdf_mapper_MB": [],
        "Memoria_rdflib_MB": [],
    }

    for VOLUME in VOLUMES:
        print(f"\nVolume de entidades: {VOLUME}")

        # --- rdflib puro ---
        print("Populando rdflib...")
        mem_start = memory_mb()
        g_rdflib = populate_graph(VOLUME)
        mem_after = memory_mb()
        mem_rdflib = mem_after - mem_start

        print("Consultando rdflib...")
        tempo_rdflib, _ = benchmark_rdflib_query(g_rdflib)
        print(f"Tempo consulta rdflib: {tempo_rdflib:.6f}s, Memória: {mem_rdflib:.2f} MB")

        # --- rdf_mapper ---
        print("Populando rdf_mapper...")
        mem_start = memory_mb()
        g_mapper = populate_graph_rdfmapper(VOLUME)
        mem_after = memory_mb()
        mem_mapper = mem_after - mem_start

        print("Consultando rdf_mapper...")
        tempo_mapper, _ = benchmark_rdfmapper_query(g_mapper)
        print(f"Tempo consulta rdf_mapper: {tempo_mapper:.6f}s, Memória: {mem_mapper:.2f} MB")

        dados["Volume"].append(VOLUME)
        dados["Tempo_rdf_mapper"].append(tempo_mapper)
        dados["Tempo_rdflib"].append(tempo_rdflib)
        dados["Memoria_rdf_mapper_MB"].append(mem_mapper)
        dados["Memoria_rdflib_MB"].append(mem_rdflib)

    # -- Gráficos --
    plt.figure(figsize=(8,4))
    plt.plot(dados["Volume"], dados["Tempo_rdflib"], marker='o', label="rdflib (SPARQL)")
    plt.plot(dados["Volume"], dados["Tempo_rdf_mapper"], marker='o', label="rdf_mapper (find_by_nome)")
    plt.ylabel("Tempo de consulta (s)")
    plt.xlabel("Volume de entidades")
    plt.title("Tempo de consulta por volume")
    plt.legend()
    plt.tight_layout()
    plt.savefig("tempo_consulta.png")
    plt.show()

    plt.figure(figsize=(8,4))
    plt.plot(dados["Volume"], dados["Memoria_rdflib_MB"], marker='o', label="rdflib")
    plt.plot(dados["Volume"], dados["Memoria_rdf_mapper_MB"], marker='o', label="rdf_mapper")
    plt.ylabel("Memória utilizada (MB)")
    plt.xlabel("Volume de entidades")
    plt.title("Memória utilizada por volume")
    plt.legend()
    plt.tight_layout()
    plt.savefig("memoria_utilizada.png")
    plt.show()

    # Salva CSV
    try:
        import pandas as pd
        pd.DataFrame(dados).to_csv("bench_consulta.csv", index=False)
    except ImportError:
        pass

    print("Benchmark finalizado. Gráficos e CSV salvos.")

