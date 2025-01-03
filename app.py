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
        print("Tentativa de acesso à rota '/', mas conexão com MongoDB falhou")
        return jsonify({"status": "erro", "mensagem": "Conexão com MongoDB falhou"}), 500
    print("A rota '/' foi acessada com sucesso")
    return jsonify({"status": "sucesso", "mensagem": "API funcionando"}), 200

@app.route('/data', methods=['GET'])
def get_data():
    if client is None:
        print("Tentativa de acesso à rota '/data', mas conexão com MongoDB falhou")
        return jsonify({"status": "erro", "mensagem": "Conexão com MongoDB falhou"}), 500
    try:
        print("Rota '/data' acessada")

        filtro = request.args.get("filter", "{}")
        campos = request.args.get("fields", "{}")
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10000))

        print(f"Parâmetros recebidos: filtro={filtro}, campos={campos}, page={page}, limit={limit}")

        filtro = json.loads(filtro) if filtro else {}
        campos = json.loads(campos) if campos else {"_id": 1, "data": 1, "event": 1, "timestamp": 1, "website_id": 1}

        skip = (page - 1) * limit

        cursor = collection.find(filtro, campos).skip(skip).limit(limit)
        data = []

        for item in cursor:
            if "_id" in item:
                item["_id"] = str(item["_id"])
            if "timestamp" in item:
                item["timestamp"] = int(item["timestamp"])
            data.append(item)

        print(f"Dados retornados (tamanho={len(data)}): Página {page}")
        return jsonify({"status": "sucesso", "data": data, "page": page, "limit": limit}), 200
    except Exception as e:
        error_message = {
            "status": "erro",
            "mensagem": str(e),
            "trace": traceback.format_exc()
        }
        print(f"Erro na rota '/data': {error_message}")
        return jsonify(error_message), 500

if __name__ == '__main__':
    print("Iniciando o servidor Flask...")
    port = int(os.environ.get("PORT", 80))
    print(f"Servidor escutando na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
