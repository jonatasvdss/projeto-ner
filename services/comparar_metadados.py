import re
import difflib
import unicodedata

import pandas as pd

from services.gerenciador_documento import GerenciadorDocumento
from services.resultado_comparacao import Resultado


def normalizar_id(id_val):
    if pd.isna(id_val) or id_val == "" or id_val == "0":
        return ""
    
    s = str(id_val)
    apenas_digitos = re.sub(r"[^\d]", "", s)

    return str(int(apenas_digitos)) if apenas_digitos else ""


def normalizar_nome(nome):
    if pd.isna(nome) or nome == "":
        return ""
    
    s = str(nome).strip().lower()
    s = re.sub(r'[^\w\s]', '', s)
    nfkd_form = unicodedata.normalize('NFKD', s)

    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def calcular_similaridade(texto1, texto2):
    return difflib.SequenceMatcher(None, texto1, texto2).ratio()


def peticao_contem_metadados(
        peticao: str,
        meta_nome_autor: str,
        meta_id_autor: str | int,
        meta_nome_reu: str,
        meta_id_reu: str | int
    ) -> Resultado:
    """
    Compara os metadados fornecidos com os nomes, CPFs e CNPJs reconhecidos na petição inicial
    por modelos spaCy e BERT.

    Se algum dos metadados contiver mais de um valor, deve-se separá-los com "#".
    Ex.: meta_nome_autor="João Pedro#Maria da Silva#Gabriel Vilela".

    :param peticao: Texto da petição inicial.
    :type peticao: str
    :param meta_nome_autor: Nome(s) do(s) polo(s) ativo(s).
    :type meta_nome_autor: str
    :param meta_id_autor: Identificador(es) do(s) polo(s) ativo(s).
    :type meta_id_autor: str | int
    :param meta_nome_reu: Nome(s) do(s) polo(s) passivo(s).
    :type meta_nome_reu: str
    :param meta_id_reu: Identificador(es) do(s) polo(s) passivo(s).
    :type meta_id_reu: str | int

    :return: Objeto contendo os resultados da auditoria com os seguintes atributos:

        * **sucesso_geral (bool):** Indica se todos os metadados esperados foram encontrados.
        * **comparacao_ids (list[dict]):** Lista detalhada da verificação de cada CPF/CNPJ.
        * **comparacao_nomes (list[dict]):** Lista detalhada da verificação de cada nome.
        * **ids_extraidos (list[str]):** Lista bruta de todos os IDs encontrados pelos modelos.
        * **nomes_extraidos (list[str]):** Lista bruta de todos os nomes encontrados pelos modelos.
    :rtype: services.resultado_comparacao.Resultado
    """

    if pd.isna(peticao):
        peticao_limpa = ""
    else:
        s = str(peticao).replace(">>>>>inicio<<<<<", "")
        s = re.sub(r"#####fim#####.*", "", s)
        peticao_limpa = re.sub(r'\s+', ' ', s).strip()
    
    processor = GerenciadorDocumento(peticao_limpa)
    processor.preprocessar()
    processor.extrair_entidades()
    processor.extrair_entidades_bert()
    entidades_extraidas = processor.get_entidades()
    
    pool_ids_encontrados = set()
    pool_nomes_encontrados_bruto = set()

    for ent in entidades_extraidas:
        if ent["label"] in ["CPF", "CNPJ"]:
            pool_ids_encontrados.add(normalizar_id(ent["texto"]))
        elif ent["label"] in ["PESSOA", "ORGANIZACAO"]:
            pool_nomes_encontrados_bruto.add(normalizar_nome(ent["texto"]))

    lista_nomes_ordenada = sorted(list(pool_nomes_encontrados_bruto), key=len, reverse=True)
    pool_nomes_encontrados = set()
    for nome in lista_nomes_ordenada:
        if not any(nome in nome_maior for nome_maior in pool_nomes_encontrados):
            pool_nomes_encontrados.add(nome)

    def listar_metadados_esperados(valor_bruto, tipo):
        lista_final = []

        if pd.isna(valor_bruto):
            return lista_final
        
        valores = str(valor_bruto).split("#")

        for valor in valores:
            norm = normalizar_id(valor) if tipo == 'id' else normalizar_nome(valor)
            if norm:
                lista_final.append(norm)

        return lista_final

    ids_esperados = (
        listar_metadados_esperados(meta_id_autor, 'id')
        + listar_metadados_esperados(meta_id_reu, 'id')
        )
    nomes_esperados = (
        listar_metadados_esperados(meta_nome_autor, 'nome')
        + listar_metadados_esperados(meta_nome_reu, 'nome')
        )

    todos_encontrados = True
    
    detalhes_ids = []
    detalhes_nomes = []
    
    LIMIAR_SIMILARIDADE = 0.85

    for id_target in ids_esperados:
        encontrado = id_target in pool_ids_encontrados
        
        status_texto = "ENCONTRADO" if encontrado else "AUSENTE"
        classe_css = "sucesso" if encontrado else "erro"
        
        detalhes_ids.append({
            'alvo': id_target,
            'status': status_texto,
            'classe': classe_css
        })
        
        if not encontrado:
            todos_encontrados = False

    for nome_target in nomes_esperados:
        encontrado = False
        match_info = ""
        
        if nome_target in pool_nomes_encontrados:
            encontrado = True
            match_info = "(Exato)"
        else:
            for nome_extraido in pool_nomes_encontrados:
                if nome_target in nome_extraido:
                    encontrado = True
                    match_info = "(Contido)"
                    break
                
                if len(nome_extraido) > 2:
                    padrao = r"\b" + re.escape(nome_extraido) + r"\b"

                    if re.search(padrao, nome_target):
                        encontrado = True
                        match_info = "(Parcial)"
                        break
                
                tokens_target = set(nome_target.split())
                tokens_extraido = set(nome_extraido.split())
                interseccao = tokens_target.intersection(tokens_extraido)

                if len(tokens_target) > 0:
                    ratio_token = len(interseccao) / len(tokens_target)

                    if len(interseccao) >= 2 and ratio_token >= 0.6:
                        encontrado = True
                        match_info = f"(Tokens {len(interseccao)}/{len(tokens_target)})"
                        break

                score = calcular_similaridade(nome_target, nome_extraido)

                if score >= LIMIAR_SIMILARIDADE:
                    encontrado = True
                    match_info = f"(Similaridade {score:.2f})"
                    break
        
        status_texto = f"ENCONTRADO {match_info}" if encontrado else "AUSENTE"
        classe_css = "sucesso" if encontrado else "erro"
        
        detalhes_nomes.append({
            'alvo': nome_target,
            'status': status_texto,
            'classe': classe_css
        })
        
        if not encontrado:
            todos_encontrados = False

    resultado_final = Resultado(
            sucesso_geral=todos_encontrados,
            comparacao_ids=detalhes_ids,
            comparacao_nomes=detalhes_nomes,
            ids_extraidos=sorted(list(pool_ids_encontrados)),
            nomes_extraidos=sorted(list(pool_nomes_encontrados))
            )

    return resultado_final