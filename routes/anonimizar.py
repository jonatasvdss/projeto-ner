from flask import Blueprint, jsonify, request
from services.gerenciador_documento import GerenciadorDocumento
from time import time

anonimizar_bp = Blueprint('anonimizar', __name__)

@anonimizar_bp.route('/anonimizar', methods=['POST'])
def anonimizar():
    requisitar_dados = request.get_json()
    texto = requisitar_dados.get('texto', '')
    
    if not texto:
        return jsonify({'ERRO': 'Texto não fornecido'}), 400
    
    start = time()
    processor = GerenciadorDocumento(texto)
    end = time()
    print(f"Tempo para instanciar a classe GerenciadorDocumento = {end - start}")
    processor.preprocessar()
    end = time()
    print(f"Tempo para preprocessar = {end - start}")
    processor.extrair_entidades()
    processor.extrair_entidades_bert()
    end = time()
    print(f"Tempo para extrair entidades = {end - start}")
    entidades = processor.get_entidades()
    end = time()
    print(f"Tempo para get entidades = {end - start}")
    texto_anonimizado = processor.anonimizar_texto()
    end = time()
    print(f"Tempo para anonimizar texto = {end - start}")
    end = time()
    print('---------------------------------------------------------------------------\n\n')
    entidades = processor.get_entidades()
    
    return jsonify({'texto_anonimizado': texto_anonimizado, 'entidades': entidades})