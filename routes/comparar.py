# Rota implementada por Jônatas Vicente da Silva

from flask import Blueprint, render_template, request
from comparar_metadados import peticao_contem_metadados

comparar_bp = Blueprint('comparar', __name__)

@comparar_bp.route('/comparar_peticao_metadados', methods=['GET', 'POST'])
def index():
    # meta_nome_autor = request.form['meta_nome_autor']
    # meta_nome_reu = request.form['meta_nome_reu']
    # meta_id_autor = request.form['meta_id_autor']
    # meta_id_reu = request.form['meta_id_reu']
    # peticao = request.files['peticao']

    # Converter pdf em texto...

    # peticao_contem_metadados(peticao, meta_nome_autor, meta_nome_reu, meta_id_autor, meta_id_reu)

    return render_template('index.html')