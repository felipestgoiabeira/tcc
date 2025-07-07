from rdflib import Namespace
from rdf_mapper.rdf_mapper import RDFMapper
from rdf_mapper.rdf_repository import RDFRepository
from rdflib import Graph

NAMESPACE = "https://dados.gov.br/dados/conjuntos-dados/serie-historica-de-precos-de-combustiveis-e-de-glp#"
EX = Namespace(NAMESPACE)
rdf_mapper = RDFMapper()

@rdf_mapper.rdf_entity(EX.Combustiveis)
class Combustiveis:
    def __init__(self,  uri, Regiao___Sigla, Estado___Sigla, Municipio, Revenda, CNPJ_da_Revenda, Nome_da_Rua, Numero_Rua, Complemento, Bairro, Cep, Produto, Data_da_Coleta, Valor_de_Venda, Valor_de_Compra, Unidade_de_Medida, Bandeira):
        self.uri = uri
        self._Regiao___Sigla: str = Regiao___Sigla
        self._Estado___Sigla: str = Estado___Sigla
        self._Municipio: str = Municipio
        self._Revenda: str = Revenda
        self._CNPJ_da_Revenda: str = CNPJ_da_Revenda
        self._Nome_da_Rua: str = Nome_da_Rua
        self._Numero_Rua: str = Numero_Rua
        self._Complemento: str = Complemento
        self._Bairro: str = Bairro
        self._Cep: str = Cep
        self._Produto: str = Produto
        self._Data_da_Coleta: str = Data_da_Coleta
        self._Valor_de_Venda: str = Valor_de_Venda
        self._Valor_de_Compra: str = Valor_de_Compra
        self._Unidade_de_Medida: str = Unidade_de_Medida
        self._Bandeira: str = Bandeira

    @rdf_mapper.rdf_property(EX.Regiao___Sigla)
    def Regiao___Sigla(self):
        return self._Regiao___Sigla

    @rdf_mapper.rdf_property(EX.Estado___Sigla)
    def Estado___Sigla(self):
        return self._Estado___Sigla

    @rdf_mapper.rdf_property(EX.Municipio)
    def Municipio(self):
        return self._Municipio

    @rdf_mapper.rdf_property(EX.Revenda)
    def Revenda(self):
        return self._Revenda

    @rdf_mapper.rdf_property(EX.CNPJ_da_Revenda)
    def CNPJ_da_Revenda(self):
        return self._CNPJ_da_Revenda

    @rdf_mapper.rdf_property(EX.Nome_da_Rua)
    def Nome_da_Rua(self):
        return self._Nome_da_Rua

    @rdf_mapper.rdf_property(EX.Numero_Rua)
    def Numero_Rua(self):
        return self._Numero_Rua

    @rdf_mapper.rdf_property(EX.Complemento)
    def Complemento(self):
        return self._Complemento

    @rdf_mapper.rdf_property(EX.Bairro)
    def Bairro(self):
        return self._Bairro

    @rdf_mapper.rdf_property(EX.Cep)
    def Cep(self):
        return self._Cep

    @rdf_mapper.rdf_property(EX.Produto)
    def Produto(self):
        return self._Produto

    @rdf_mapper.rdf_property(EX.Data_da_Coleta)
    def Data_da_Coleta(self):
        return self._Data_da_Coleta

    @rdf_mapper.rdf_property(EX.Valor_de_Venda)
    def Valor_de_Venda(self):
        return self._Valor_de_Venda

    @rdf_mapper.rdf_property(EX.Valor_de_Compra)
    def Valor_de_Compra(self):
        return self._Valor_de_Compra

    @rdf_mapper.rdf_property(EX.Unidade_de_Medida)
    def Unidade_de_Medida(self):
        return self._Unidade_de_Medida

    @rdf_mapper.rdf_property(EX.Bandeira)
    def Bandeira(self):
        return self._Bandeira


if __name__ == "__main__":
    import pandas as pd
    import csv

    df = pd.read_csv(
        'tests/dados_abertos/gov_combustiveis/Preços semestrais - AUTOMOTIVOS_2024.02.csv',
        sep=';',
        usecols=lambda c: not c.startswith('Unnamed'),
        quoting=csv.QUOTE_NONE,
        on_bad_lines='warn'
    )

    combustiveis_list = []

    for i, row in df.iterrows():
        uri = f"{NAMESPACE}:{i}"
        obj = Combustiveis(
            uri=uri,
            Regiao___Sigla = row["Regiao - Sigla"],
            Estado___Sigla = row["Estado - Sigla"],
            Municipio = row["Municipio"],
            Revenda = row["Revenda"],
            CNPJ_da_Revenda = row["CNPJ da Revenda"],
            Nome_da_Rua = row["Nome da Rua"],
            Numero_Rua = row["Numero Rua"],
            Complemento = row["Complemento"],
            Bairro = row["Bairro"],
            Cep = row["Cep"],
            Produto = row["Produto"],
            Data_da_Coleta = row["Data da Coleta"],
            Valor_de_Venda = row["Valor de Venda"],
            Valor_de_Compra = row["Valor de Compra"],
            Unidade_de_Medida = row["Unidade de Medida"],
            Bandeira = row["Bandeira"]
        )
        combustiveis_list.append(obj)


    graph = rdf_mapper.to_rdf_many(combustiveis_list)
    graph.bind("ex", EX)
    graph.serialize(
        destination="precos-combustiveis.rdf",
        format="application/rdf+xml"
    )

    # repo = RDFRepository(rdf_mapper, graph, Combustiveis)
    # results = repo.group_by_count(Combustiveis, "curso")

    # for row in results:
    #     print(f"{row['curso']}: {row['count']} TCCs")
