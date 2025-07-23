from rdflib import Namespace
from src.rdf_mapper.rdf_mapper import RDFMapper
from src.rdf_mapper.rdf_repository import RDFRepository
from rdflib import Graph
import matplotlib.pyplot as plt

EX = Namespace("https://dadosabertos.ufma.br/dataset/trabalhos-de-conclusao-de-curso-defendidos#")
rdf_mapper = RDFMapper()

@rdf_mapper.rdf_entity(EX.TCC)
class TCC:
    def __init__(
        self, uri,
        municipio=None, curso=None, turno=None, modalidade=None,
        nivel=None, mes=None, ano=None,
        titulo=None, autor=None, orientador=None,
        tipo=None, data_defesa=None
    ):
        self.uri = uri
        self._municipio = municipio
        self._curso = curso
        self._turno = turno
        self._modalidade = modalidade
        self._nivel = nivel
        self._mes = mes
        self._ano = ano
        self._titulo = titulo
        self._autor = autor
        self._orientador = orientador
        self._tipo = tipo
        self._data_defesa = data_defesa

    @rdf_mapper.rdf_property(EX.municipio)
    def municipio(self): pass

    @rdf_mapper.rdf_property(EX.curso)
    def curso(self): pass

    @rdf_mapper.rdf_property(EX.turno)
    def turno(self): pass

    @rdf_mapper.rdf_property(EX.modalidade)
    def modalidade(self): pass

    @rdf_mapper.rdf_property(EX.nivel)
    def nivel(self): pass

    @rdf_mapper.rdf_property(EX.mes)
    def mes(self): pass

    @rdf_mapper.rdf_property(EX.ano)
    def ano(self): pass

    @rdf_mapper.rdf_property(EX.titulo)
    def titulo(self): pass

    @rdf_mapper.rdf_property(EX.autor)
    def autor(self): pass

    @rdf_mapper.rdf_property(EX.orientador)
    def orientador(self): pass

    @rdf_mapper.rdf_property(EX.tipo)
    def tipo(self): pass

    @rdf_mapper.rdf_property(EX.data_defesa)
    def data_defesa(self): pass


if __name__ == "__main__":
    import pandas as pd
    import csv

    df = pd.read_csv(
        'src/tests/dados_abertos/ufma_trabalho_conclusao_curso/defesas_de_dissertacao_e_tese-2024.2.csv',
        sep=';',
        usecols=lambda c: not c.startswith('Unnamed'),
        quoting=csv.QUOTE_NONE,
        on_bad_lines='warn'
    )

    tcc_list = []

    for i, row in df.iterrows():
        uri = f"https://dadosabertos.ufma.br/dataset/trabalhos-de-conclusao-de-curso-defendidos:{i}"
        tcc = TCC(
            uri=uri,
            municipio=row['municipio'],
            curso=row['curso'],
            turno=row['turno'],
            modalidade=row['modalidade'],
            nivel=row['nivel'],
            mes=row['mes'],
            ano=row['ano'],
            titulo=row['titulo'],
            autor=row['autor'],
            orientador=row['orientador'],
            tipo=row['tipo'],
            data_defesa=row['data_defesa']
        )
        tcc_list.append(tcc)


    graph = rdf_mapper.to_rdf_many(tcc_list)
    graph.bind("ex", EX)
    # graph.serialize(
    #     destination="trabalhos-de-conclusao-de-curso-defendidos.rdf",
    #     format="application/rdf+xml"
    # )

    repo = RDFRepository(rdf_mapper, graph, TCC)

    

    results = repo.group_by_count(TCC, "curso", order="DESC")
    cursos = [row["curso"] for row in results][:10]
    counts = [row["count"] for row in results][:10]

    plt.figure(figsize=(10, 6))
    plt.barh(cursos[::-1], counts[::-1])
    plt.xlabel("Quantidade de TCCs")
    plt.title("Top 10 Cursos por Volume de TCCs")
    plt.tight_layout()
    plt.savefig("imagens_tcc/tccs_por_curso.png")


    results = repo.group_by_count(TCC, "modalidade", order="DESC")
    modalidades = [row["modalidade"] for row in results]
    counts = [row["count"] for row in results]

    plt.figure()
    plt.pie(counts, labels=modalidades, autopct="%1.1f%%", startangle=140)
    plt.title("Distribuição por Modalidade")
    plt.tight_layout()
    plt.savefig("imagens_tcc/modalidade_pizza.png")

    results = repo.group_by_count(TCC, "municipio", order="desc")
    municipios = [row["municipio"] for row in results][:10]
    counts = [row["count"] for row in results][:10]

    plt.figure(figsize=(10, 6))
    plt.barh(municipios[::-1], counts[::-1])
    plt.xlabel("Quantidade de TCCs")
    plt.title("Top 10 Municípios com mais Defesas")
    plt.tight_layout()
    plt.savefig("imagens_tcc/tccs_por_municipio.png")

    results = repo.group_by_count(TCC, "mes", order="DESC")
    mes = [row["mes"] for row in results]
    counts = [row["count"] for row in results]

    plt.figure()
    plt.bar(mes, counts)
    plt.xlabel("mes")
    plt.ylabel("TCCs Defendidos")
    plt.title("TCCs por mes")
    plt.tight_layout()
    plt.savefig("imagens_tcc/tccs_por_mes.png")