from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import json
import traceback

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGODB_URI")
try:
    client = MongoClient(MONGO_URI)
    client.server_info()
    print("Conexão com MongoDB bem-sucedida")
except Exception as e:
    print(f"Erro ao conectar ao MongoDB: {e}")
    client = None

db = client["Assuntos"] if client is not None else None
collection = db["Crisp.Assuntos Crisp"] if db is not None else None

@app.route('/', methods=['GET'])
def home():
    if client is None:
        return jsonify({"status": "erro", "mensagem": "Conexão com MongoDB falhou"}), 500
    return jsonify({"status": "sucesso", "mensagem": "API funcionando"}), 200

@app.route('/data', methods=['GET'])
def get_data():
    if client is None:
        return jsonify({"status": "erro", "mensagem": "Conexão com MongoDB falhou"}), 500
    try:
        filtro = request.args.get("filter", "{}")
        campos = request.args.get("fields", "{}")
        filtro = json.loads(filtro) if filtro else {}
        campos = json.loads(campos) if campos else {"_id": 1}
        data = list(collection.find(filtro, campos))
        data = [
            {**item, "_id": str(item["_id"])} for item in data if "_id" in item
        ]
        return jsonify({"status": "sucesso", "data": data}), 200
    except Exception as e:
        error_message = {
            "status": "erro",
            "mensagem": str(e),
            "trace": traceback.format_exc()
        }
        return jsonify(error_message), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 80))
    app.run(host='0.0.0.0', port=port, debug=True)
