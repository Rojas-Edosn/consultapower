from flask import Flask, request, jsonify
import pyodbc
import os

app = Flask(__name__)

DB_CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")

@app.route('/data', methods=['GET'])
def get_data():
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        query = "SELECT * FROM CrispAssuntos"
        cursor.execute(query)
        rows = cursor.fetchall()
        data = []
        for row in rows:
            data.append(dict(zip([column[0] for column in cursor.description], row)))
        conn.close()
        return jsonify({"status": "sucesso", "data": data}), 200
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 80))
    app.run(host='0.0.0.0', port=port, debug=True)
