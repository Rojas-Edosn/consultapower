from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import json
import traceback

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client["Assuntos"]
collection = db["Crisp.Assuntos Crisp"]

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "sucesso", "mensagem": "API funcionando"}), 200

@app.route('/test-db', methods=['GET'])
def test_db():
    try:
        client.server_info()
        return jsonify({"status": "sucesso", "mensagem": "Conexão com MongoDB bem-sucedida"}), 200
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/data', methods=['GET'])
def get_data():
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
