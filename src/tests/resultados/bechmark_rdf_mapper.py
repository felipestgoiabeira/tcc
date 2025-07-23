import time
import tracemalloc
import gc
from rdflib import Namespace, Literal, URIRef
import matplotlib.pyplot as plt
import pandas as pd

# Supondo que você tem sua classe RDFMapper no seu projeto
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

# --- Benchmark Functions ---

def serialize_with_rdf_mapper(n):
    g = rdf_mapper.create_graph() if hasattr(rdf_mapper, 'create_graph') else None
    objs = []
    for i in range(n):
        end = Endereco(EX[f"endereco/{i}"], "Rua Exemplo")
        pes = Pessoa(EX[f"pessoa/{i}"], f"Pessoa {i}", end)
        # Serializa cada objeto (no mesmo grafo, se possível)
        g = rdf_mapper.to_rdf(pes)
        objs.append(pes)
    return g

# Versão baseline usando rdflib puro
from rdflib import Graph

def serialize_with_rdflib(n):
    g = Graph()
    for i in range(n):
        pes_uri = URIRef(EX[f"pessoa/{i}"])
        end_uri = URIRef(EX[f"endereco/{i}"])
        g.add((pes_uri, FOAF.name, Literal(f"Pessoa {i}")))
        g.add((pes_uri, EX.moradia, end_uri))
        g.add((end_uri, EX.logradouro, Literal("Rua Exemplo")))
    return g

def run_experiment(serialize_func, volumes):
    times = []
    memories = []
    for n in volumes:
        gc.collect()
        tracemalloc.start()
        start_time = time.perf_counter()
        serialize_func(n)
        duration = time.perf_counter() - start_time
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        times.append(duration)
        memories.append(peak / (1024 * 1024))  # em MB
    return times, memories

if __name__ == "__main__":
    volumes = [1000, 10000, 50000]  # Pode aumentar se quiser!
    times_mapper, mem_mapper = run_experiment(serialize_with_rdf_mapper, volumes)
    times_rdflib, mem_rdflib = run_experiment(serialize_with_rdflib, volumes)

    # Salvar gráficos
    plt.figure(figsize=(10, 5))
    plt.plot(volumes, times_mapper, marker='o', label='rdf_mapper')
    plt.plot(volumes, times_rdflib, marker='s', label='rdflib puro')
    plt.xlabel('Quantidade de Entidades')
    plt.ylabel('Tempo (s)')
    plt.title('Tempo de Inserção')
    plt.grid(True)
    plt.legend()
    plt.savefig("tempo_insercao.png")
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.plot(volumes, mem_mapper, marker='o', label='rdf_mapper')
    plt.plot(volumes, mem_rdflib, marker='s', label='rdflib puro')
    plt.xlabel('Quantidade de Entidades')
    plt.ylabel('Uso de Memória (MB)')
    plt.title('Uso de Memória')
    plt.grid(True)
    plt.legend()
    plt.savefig("uso_memoria.png")
    plt.close()

    # Exportar resultados como tabela CSV
    df = pd.DataFrame({
        "Volume": volumes,
        "Tempo_rdf_mapper": times_mapper,
        "Tempo_rdflib": times_rdflib,
        "Memoria_rdf_mapper_MB": mem_mapper,
        "Memoria_rdflib_MB": mem_rdflib
    })
    df.to_csv("resultado_benchmark.csv", index=False)
    print(df)
    print("Gráficos e tabela salvos!")
