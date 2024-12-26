from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client["Assuntos"]
collection = db["Crisp.Assuntos Crisp"]

@app.route('/data', methods=['GET'])
def get_data():
    try:
        filtro = request.args.get("filter", "{}")
        campos = request.args.get("fields", "{}")
        filtro = eval(filtro) if filtro else {}
        campos = eval(campos) if campos else {"_id": 0}
        data = list(collection.find(filtro, campos))
        return jsonify({"status": "sucesso", "data": data}), 200
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
