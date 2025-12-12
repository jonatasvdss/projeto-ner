from flask import Blueprint, render_template, request
from services.comparar_metadados import peticao_contem_metadados
import pdfplumber
import logging

comparar_bp = Blueprint('comparar', __name__)

@comparar_bp.route('/comparar_peticao_metadados', methods=['GET', 'POST'])
def index():
    resultado = None
    excecao = None
    
    if request.method == 'POST':
        try:
            if 'peticao' not in request.files:
                return render_template('index.html', resultado=None, excecao="Nenhum arquivo enviado.")

            peticao_arquivo = request.files['peticao']
            
            meta_nome_autor = request.form.get('meta_nome_autor', '')
            meta_nome_reu = request.form.get('meta_nome_reu', '')
            meta_id_autor = request.form.get('meta_id_autor', '')
            meta_id_reu = request.form.get('meta_id_reu', '')

            peticao_texto = ''
            
            with pdfplumber.open(peticao_arquivo.stream) as pdf:
                for pagina in pdf.pages:
                    texto_pagina = pagina.extract_text(x_tolerance=3) or ""
                    peticao_texto += texto_pagina + '\n'

            resultado = peticao_contem_metadados(
                peticao_texto,
                meta_nome_autor,
                meta_id_autor,
                meta_nome_reu,
                meta_id_reu
            )
            
        except Exception as e:
            logging.error(f"Erro ao processar petição: {e}")
            excecao = str(e)
            return render_template('index.html', resultado=None, excecao=excecao)

    return render_template('index.html', resultado=resultado, excecao=excecao)