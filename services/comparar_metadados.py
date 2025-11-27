import pandas as pd
import re
import difflib
import unicodedata
from services.gerenciador_documento import GerenciadorDocumento

# ... (Mantenha as funções auxiliares normalizar_id, normalizar_nome e calcular_similaridade iguais) ...
def normalizar_id(id_val):
    if pd.isna(id_val) or id_val == "": return ""
    s = str(id_val)
    if s.endswith(".0"): s = s[:-2]
    apenas_digitos = re.sub(r"[^\d]", "", s)
    return str(int(apenas_digitos)) if apenas_digitos else ""

def normalizar_nome(nome):
    if pd.isna(nome) or nome == "": return ""
    s = str(nome).strip().lower()
    s = re.sub(r'[^\w\s]', '', s)
    nfkd_form = unicodedata.normalize('NFKD', s)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def calcular_similaridade(texto1, texto2):
    return difflib.SequenceMatcher(None, texto1, texto2).ratio()

def peticao_contem_metadados(
        peticao: str, 
        meta_nome_autor: str, 
        meta_id_autor, 
        meta_nome_reu: str, 
        meta_id_reu
    ) -> tuple[dict, bool]:  # <--- Mudança no tipo de retorno
    
    # ... (Mantenha a lógica de limpeza inicial da petição igual) ...
    if pd.isna(peticao):
        peticao_limpa = ""
    else:
        s = str(peticao).replace(">>>>>inicio<<<<<", "")
        s = re.sub(r"#####fim#####.*", "", s)
        peticao_limpa = re.sub(r'\s+', ' ', s).strip()
    
    # ... (Mantenha o processamento e extração igual) ...
    processor = GerenciadorDocumento(peticao_limpa)
    processor.preprocessar()
    processor.extrair_entidades()
    processor.extrair_entidades_bert()
    processor.extrair_entidades_lgpd()
    entidades_extraidas = processor.get_entidades()
    
    # ... (Mantenha a construção dos pools igual) ...
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

    # ... (Mantenha a preparação dos metadados igual) ...
    def listar_metadados_esperados(valor_bruto, tipo):
        lista_final = []
        if pd.isna(valor_bruto): return lista_final
        valores = str(valor_bruto).split("#")
        for v in valores:
            norm = normalizar_id(v) if tipo == 'id' else normalizar_nome(v)
            if norm: lista_final.append(norm)
        return lista_final

    ids_esperados = (listar_metadados_esperados(meta_id_autor, 'id') + listar_metadados_esperados(meta_id_reu, 'id'))
    nomes_esperados = (listar_metadados_esperados(meta_nome_autor, 'nome') + listar_metadados_esperados(meta_nome_reu, 'nome'))

    # --- 4. Verificação e Construção do Objeto de Resposta ---
    todos_encontrados = True
    
    # Listas de dicionários para o HTML
    detalhes_ids = []
    detalhes_nomes = []
    
    LIMIAR_SIMILARIDADE = 0.85 

    # --- Verificação IDs ---
    for id_target in ids_esperados:
        encontrado = id_target in pool_ids_encontrados
        
        # Define classe CSS e texto baseado no resultado
        status_texto = "ENCONTRADO" if encontrado else "AUSENTE"
        classe_css = "sucesso" if encontrado else "erro"
        
        detalhes_ids.append({
            'alvo': id_target,
            'status': status_texto,
            'classe': classe_css
        })
        
        if not encontrado:
            todos_encontrados = False

    # --- Verificação Nomes ---
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

    # 5. Retorno Estruturado
    resultado_final = {
        'sucesso_geral': todos_encontrados,
        'comparacao_ids': detalhes_ids,
        'comparacao_nomes': detalhes_nomes,
        'ids_extraidos': sorted(list(pool_ids_encontrados)),
        'nomes_extraidos': sorted(list(pool_nomes_encontrados))
    }

    return resultado_final, todos_encontrados