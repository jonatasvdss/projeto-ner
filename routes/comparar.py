# Rota implementada por Jônatas Vicente da Silva

from flask import Blueprint, render_template, request
from services.comparar_metadados import peticao_contem_metadados
from pypdf import PdfReader

comparar_bp = Blueprint('comparar', __name__)

@comparar_bp.route('/comparar_peticao_metadados', methods=['GET', 'POST'])
def index():
    resultado = None
    
    if request.method == 'GET':
        ...
    
    if request.method == 'POST':
        peticao_arquivo = request.files['peticao']
        
        meta_nome_autor = request.form['meta_nome_autor']
        meta_nome_reu = request.form['meta_nome_reu']
        meta_id_autor = request.form['meta_id_autor']
        meta_id_reu = request.form['meta_id_reu']

        leitor_pdf = PdfReader(peticao_arquivo.stream)

        peticao_texto = ''

        for pagina in leitor_pdf.pages:
            texto_pagina = pagina.extract_text()
            peticao_texto += texto_pagina + '\n'

        resultado, _ = peticao_contem_metadados(
            peticao_texto,
            meta_nome_autor,
            meta_id_autor,
            meta_nome_reu,
            meta_id_reu
            )

    return render_template('index.html', resultado=resultado)