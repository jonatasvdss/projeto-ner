import pandas as pd
import re
import difflib
import unicodedata
from services.gerenciador_documento import GerenciadorDocumento

def normalizar_id(id_val):
    """Normaliza CPF/CNPJ."""
    if pd.isna(id_val) or id_val == "":
        return ""
    s = str(id_val)
    if s.endswith(".0"):
        s = s[:-2]
    apenas_digitos = re.sub(r"[^\d]", "", s)
    return str(int(apenas_digitos)) if apenas_digitos else ""

def normalizar_nome(nome):
    """
    Converte para minúsculas, remove acentos e pontuação.
    """
    if pd.isna(nome) or nome == "":
        return ""
    
    s = str(nome).strip().lower()
    s = re.sub(r'[^\w\s]', '', s) # Remove pontuação
    nfkd_form = unicodedata.normalize('NFKD', s)
    nome_limpo = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    
    return nome_limpo

def calcular_similaridade(texto1, texto2):
    """
    Retorna pontuação de 0.0 a 1.0.
    """
    return difflib.SequenceMatcher(None, texto1, texto2).ratio()

def peticao_contem_metadados(
        peticao: str, 
        meta_nome_autor: str, 
        meta_id_autor, 
        meta_nome_reu: str, 
        meta_id_reu
    ) -> bool:
    
    # --- CORREÇÃO CRÍTICA: Limpeza de Marcadores e Espaços ---
    if pd.isna(peticao):
        peticao_limpa = ""
    else:
        s = str(peticao)
        
        # 1. Remove a tag de início identificada como causadora do erro
        s = s.replace(">>>>>inicio<<<<<", "")
        
        # 2. (Opcional/Preventivo) Remove a tag de fim e o ID que vem depois
        s = re.sub(r"#####fim#####.*", "", s)
        
        # 3. Limpeza agressiva de whitespace (CR LF, tabs e espaços múltiplos viram 1 espaço)
        peticao_limpa = re.sub(r'\s+', ' ', s).strip()
    
    # 1. Processamento da Petição (agora com texto limpo)
    processor = GerenciadorDocumento(peticao_limpa)
    processor.preprocessar()
    processor.extrair_entidades()
    processor.extrair_entidades_bert()
    processor.extrair_entidades_lgpd()

    
    entidades_extraidas = processor.get_entidades()
    
    # 2. Construção do Pool de Busca
    pool_ids_encontrados = set()
    pool_nomes_encontrados_bruto = set()
    
    for ent in entidades_extraidas:
        rotulo = ent["label"]
        texto = ent["texto"]
        
        if rotulo in ["CPF", "CNPJ"]:
            pool_ids_encontrados.add(normalizar_id(texto))
        elif rotulo in ["PESSOA", "ORGANIZACAO"]:
            pool_nomes_encontrados_bruto.add(normalizar_nome(texto))

    # Limpeza de fragmentos
    lista_nomes_ordenada = sorted(list(pool_nomes_encontrados_bruto), key=len, reverse=True)
    pool_nomes_encontrados = set()

    for nome in lista_nomes_ordenada:
        eh_fragmento = any(nome in nome_maior for nome_maior in pool_nomes_encontrados)
        if not eh_fragmento:
            pool_nomes_encontrados.add(nome)

    # 3. Preparação dos Metadados
    def listar_metadados_esperados(valor_bruto, tipo):
        lista_final = []
        if pd.isna(valor_bruto):
            return lista_final
        valores = str(valor_bruto).split("#")
        for v in valores:
            norm = normalizar_id(v) if tipo == 'id' else normalizar_nome(v)
            if norm:
                lista_final.append(norm)
        return lista_final

    ids_esperados = (listar_metadados_esperados(meta_id_autor, 'id') + 
                     listar_metadados_esperados(meta_id_reu, 'id'))
    
    nomes_esperados = (listar_metadados_esperados(meta_nome_autor, 'nome') + 
                       listar_metadados_esperados(meta_nome_reu, 'nome'))

    # 4. Verificação
    todos_encontrados = True
    logs_comparacao = []
    largura_fixa = 55
    LIMIAR_SIMILARIDADE = 0.85 

    # --- IDs ---
    for id_target in ids_esperados:
        encontrado = id_target in pool_ids_encontrados
        status = "✅ ENCONTRADO" if encontrado else "❌ AUSENTE   "
        logs_comparacao.append(f"[ID]   Alvo: {id_target:<{largura_fixa}} | Status: {status}")
        if not encontrado:
            todos_encontrados = False

    # --- Nomes ---
    for nome_target in nomes_esperados:
        encontrado = False
        match_type = ""
        
        # 1. Match Exato
        if nome_target in pool_nomes_encontrados:
            encontrado = True
            match_type = "(Exato)"
        else:
            for nome_extraido in pool_nomes_encontrados:
                # 2. Metadado Contido
                if nome_target in nome_extraido:
                    encontrado = True
                    match_type = "(Contido)"
                    break
                
                # 3. Extraído Contido (Regex)
                if len(nome_extraido) > 2:
                    padrao = r"\b" + re.escape(nome_extraido) + r"\b"
                    if re.search(padrao, nome_target):
                        encontrado = True
                        match_type = "(Parcial)"
                        break
                
                # 4. Interseção de Tokens
                tokens_target = set(nome_target.split())
                tokens_extraido = set(nome_extraido.split())
                interseccao = tokens_target.intersection(tokens_extraido)
                
                if len(tokens_target) > 0:
                    ratio_token = len(interseccao) / len(tokens_target)
                    if len(interseccao) >= 2 and ratio_token >= 0.6:
                        encontrado = True
                        match_type = f"(Tokens {len(interseccao)}/{len(tokens_target)})"
                        break

                # 5. Similaridade
                score = calcular_similaridade(nome_target, nome_extraido)
                if score >= LIMIAR_SIMILARIDADE:
                    encontrado = True
                    match_type = f"(Similaridade {score:.2f})"
                    break
        
        status = f"✅ ENCONTRADO {match_type}" if encontrado else "❌ AUSENTE   "
        logs_comparacao.append(f"[NOME] Alvo: {nome_target[:largura_fixa]:<{largura_fixa}} | Status: {status}")
        
        if not encontrado:
            todos_encontrados = False

    # 5. Relatório
    print("\n" + "="*92)
    print(f"RELATÓRIO DE COMPARAÇÃO (Resultado Final: {todos_encontrados})")
    print("="*92)
    print("\n--- CHECAGEM DE METADADOS ---")
    for log in logs_comparacao:
        print(log)

    print("\n--- O QUE O MODELO EXTRAIU ---")
    print(f"IDs ({len(pool_ids_encontrados)}):")
    if pool_ids_encontrados:
        for id in sorted(list(pool_ids_encontrados)):
            print(f"   • {id}")
    else:
        print("   (Nenhum id encontrado)")
    
    print(f"Nomes ({len(pool_nomes_encontrados)}):")
    if pool_nomes_encontrados:
        for nome in sorted(list(pool_nomes_encontrados)):
            print(f"   • {nome}")
    else:
        print("   (Nenhum nome encontrado)")
    print("="*92 + "\n")

    return todos_encontrados