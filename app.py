from flask import Flask, Response, request, jsonify
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

@app.route('/stream_data', methods=['GET'])
def stream_data():
    if client is None:
        return jsonify({"status": "erro", "mensagem": "Conexão com MongoDB falhou"}), 500

    try:
        filtro = request.args.get("filter", "{}")
        campos = request.args.get("fields", "{}")
        filtro = json.loads(filtro) if filtro else {}
        campos = json.loads(campos) if campos else {"_id": 1}

        # Definindo um gerador para enviar dados em chunks
        def generate():
            cursor = collection.find(filtro, campos, no_cursor_timeout=True)
            try:
                for item in cursor:
                    item["_id"] = str(item["_id"])
                    yield json.dumps(item) + "\n"
            finally:
                cursor.close()

        return Response(generate(), content_type='application/json')
    except Exception as e:
        error_message = {
            "status": "erro",
            "mensagem": str(e),
            "trace": traceback.format_exc()
        }
        return jsonify(error_message), 500

if __name__ == '__main__':
    print("Iniciando o servidor Flask...")
    port = int(os.environ.get("PORT", 80))
    app.run(host='0.0.0.0', port=port, debug=True)
