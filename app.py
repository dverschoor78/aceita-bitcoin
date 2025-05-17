from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import dotenv
from OSM import *

CLIENT_ID = dotenv.get_key('config.env', 'OSM_CLIENT_ID')
CLIENT_SECRET = dotenv.get_key('config.env', 'OSM_CLIENT_SECRET')
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
SCOPES = [
'read_prefs',
'write_prefs',
'write_diary',
'write_api',
'write_changeset_comments',
'read_gpx',
'write_gpx',
'write_notes',
'write_redactions',
'write_blocks',
'consume_messages',
'send_messages',
'openid'
]

try:
    osm_app = OSM(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scopes=SCOPES
    )
except Exception as e:
    print(f"Erro ao inicializar OSM: {e}")

app = Flask(__name__, static_folder='static')
CORS(app)

DB_FILE_PATH = dotenv.get_key('config.env', 'DB_FILE_PATH') or 'database.db'
UPLOAD_FOLDER = os.path.join(app.static_folder, 'logos')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    with sqlite3.connect(DB_FILE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estabelecimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL,
                endereco TEXT NOT NULL,
                email TEXT,
                telefone TEXT,
                website TEXT,
                observacoes TEXT,
                aceita_lightning BOOLEAN,
                aceita_onchain BOOLEAN,
                aceita_contactless BOOLEAN,
                data_verificacao TEXT,
                logo_filename TEXT
            )
        ''')
        conn.commit()

# Rotas para páginas HTML
@app.route('/')
def serve_index():
    return send_from_directory('.', 'templates/index.html')

@app.route('/sobre')
def serve_sobre():
    return send_from_directory('.', 'templates/sobre.html')

@app.route('/carteiras')
def serve_carteiras():
    return send_from_directory('.', 'templates/carteiras.html')

@app.route('/cadastro')
def serve_cadastro():
    return send_from_directory('.', 'templates/cadastro.html')

@app.route('/materiais')
def serve_materiais():
    return send_from_directory('.', 'templates/materiais.html')

@app.route('/estabelecimentos')
def serve_estabelecimentos():
    return send_from_directory('.', 'templates/estabelecimentos.html')

# Rota para arquivos estáticos (fallback)
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('.', path)

# API: Cadastro
@app.route('/api/estabelecimentos', methods=['POST'])
def cadastrar_estabelecimento():
    data = request.form
    arquivo = request.files.get('logo')
    print(data)

    nome_arquivo = None
    if arquivo:
        nome_arquivo = f"{datetime.now().timestamp()}_{arquivo.filename}"
        caminho = os.path.join(UPLOAD_FOLDER, nome_arquivo)
        arquivo.save(caminho)
    
    node = Node(
        lat=data.get('latitude'),
        lon=data.get('longitude'),
        tags={
            'name': data.get('nome'),
            'amenity': data.get('tipo'),
            'addr:street': data.get('endereco'),
            'contact:email': data.get('email'),
            'contact:phone': data.get('telefone'),
            'website': data.get('website'),
            'description': data.get('observacoes'),
            'currency:XBT': 'yes',
            'payment:lightning': 'yes' if data.get('aceita_lightning') == 'true' else 'no',
            'payment:onchain': 'yes' if data.get('aceita_onchain') == 'true' else 'no',
            'payment:lightning_contactless': 'yes' if data.get('aceita_contactless') == 'true' else 'no',
            'source': 'Aceita Bitcoin',
            'source:date': datetime.now().strftime('%Y-%m-%d'),
            'source:website': 'https://aceitabitcoin.com.br',
        }
    )

    node_id = osm_app.post_new_node(node)
    print(f'https://master.apis.dev.openstreetmap.org/node/{node_id.text}')

    with sqlite3.connect(DB_FILE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO estabelecimentos (
                nome, tipo, endereco, email, telefone, website, observacoes,
                aceita_lightning, aceita_onchain, aceita_contactless, data_verificacao, logo_filename
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            node.tags['name'],
            node.tags['amenity'],
            node.tags['addr:street'],
            node.tags['contact:email'],
            node.tags['contact:phone'],
            node.tags['website'],
            node.tags['description'],
            node.tags['payment:lightning'] == 'yes',
            node.tags['payment:onchain'] == 'yes',
            node.tags['payment:lightning_contactless'] == 'yes',
            node.tags['source:date'],
            nome_arquivo
        ))
        conn.commit()


#
    return jsonify({"success": True, "message": "Estabelecimento cadastrado com sucesso."})

# API: Listagem
@app.route('/api/estabelecimentos', methods=['GET'])
def listar_estabelecimentos():
    with sqlite3.connect(DB_FILE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM estabelecimentos")
        estabelecimentos = [dict(row) for row in cursor.fetchall()]
        return jsonify(estabelecimentos)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=3939, debug=True)
