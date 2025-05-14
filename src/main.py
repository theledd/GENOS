import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from src.models.user import db # Certifique-se que db está inicializado aqui ou em um local central
from src.routes.user import user_bp
from src.routes.cliente_routes import cliente_bp
from src.routes.produto_routes import produto_bp
from src.routes.servico_routes import servico_bp
from src.routes.os_routes import os_bp
from src.routes.movimento_estoque_routes import movimento_estoque_bp
from src.routes.financeiro_routes import financeiro_bp
from src.routes.etiqueta_routes import etiqueta_bp
from src.routes.recibo_routes import recibo_bp
from src.routes.orcamento_routes import orcamento_bp
from src.routes.link_util_routes import link_util_bp # Importar o blueprint de Links Úteis

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'), template_folder='templates')
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Configuração do Banco de Dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(cliente_bp, url_prefix='/api')
app.register_blueprint(produto_bp, url_prefix='/api')
app.register_blueprint(servico_bp, url_prefix='/api')
app.register_blueprint(os_bp, url_prefix='/api')
app.register_blueprint(movimento_estoque_bp, url_prefix='/api')
app.register_blueprint(financeiro_bp, url_prefix='/api')
app.register_blueprint(etiqueta_bp, url_prefix='/api')
app.register_blueprint(recibo_bp, url_prefix='/api')
app.register_blueprint(orcamento_bp, url_prefix='/api')
app.register_blueprint(link_util_bp, url_prefix='/api') # Registrar o blueprint de Links Úteis

with app.app_context():
    db.create_all() # Criar tabelas se não existirem

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
