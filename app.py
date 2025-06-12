from flask import Flask, request, jsonify, render_template # type: ignore
from flask_cors import CORS # type: ignore
import json, os

app = Flask(__name__)
CORS(app)

DATA_FILE = 'dados.json'

# Garante que o arquivo de dados exista
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

@app.route('/')
def home():
    return render_template('timeline.html')

@app.route('/denuncia')
def denuncia_page():
    return render_template('denuncia.html')

@app.route('/enviar', methods=['POST'])
def enviar():
    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    anonimo = request.form.get('anonimo') == 'true'
    nome = request.form.get('nome') if not anonimo else 'Anônimo'
    contato = request.form.get('contato') if not anonimo else 'Não informado'

    nova = {
        "id": int(os.stat(DATA_FILE).st_mtime_ns),
        "titulo": titulo,
        "descricao": descricao,
        "nome": nome,
        "contato": contato,
        "status": "Pendente"
    }

    with open(DATA_FILE, 'r+', encoding='utf-8') as f:
        try:
            denuncias = json.load(f)
        except json.JSONDecodeError:
            denuncias = []
        denuncias.insert(0, nova)
        f.seek(0)
        json.dump(denuncias, f, indent=2, ensure_ascii=False)
        f.truncate()

    return jsonify({"mensagem": "Denúncia enviada com sucesso!"})

@app.route('/denuncias')
def listar():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            denuncias = json.load(f)
        except json.JSONDecodeError:
            denuncias = []
    return jsonify(denuncias)

@app.route("/contato")
def contato():
    return render_template("contato.html")

@app.route("/detalhe/<int:id>")
def detalhe(id):
    # lógica para pegar e exibir a denúncia com id
    return render_template("detalhe.html", denuncia=denuncia)


@app.route('/detalhe/<int:id>')
def detalhe(id):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        denuncias = json.load(f)
    denuncia = next((d for d in denuncias if d['id'] == id), None)
    if denuncia:
        return render_template('detalhe.html', denuncia=denuncia)
    return "Denúncia não encontrada", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
