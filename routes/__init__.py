from flask import Blueprint
from .anonimizar import anonimizar_bp

routes_bp = Blueprint('routes', __name__, url_prefix='/anonimizacao_docs')
routes_bp.register_blueprint(anonimizar_bp)