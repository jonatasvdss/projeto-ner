from dataclasses import dataclass


@dataclass
class Resultado:
    sucesso_geral: bool
    comparacao_ids: list[dict[str, str]]
    comparacao_nomes: list[dict[str, str]]
    ids_extraidos: list[str]
    nomes_extraidos: list[str]