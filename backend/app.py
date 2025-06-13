from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from api import IGDBClient
from database import criar_banco
from models.jogo import Jogo

app = Flask(__name__)
CORS(app)

criar_banco()

CLIENT_ID = "j39kwre2g3ed7doj858xjwaex7yjz5"
CLIENT_SECRET = "krpia7k46sqpg2tu9c2cn23qnny6sm"
igdb = IGDBClient(CLIENT_ID, CLIENT_SECRET)

@app.route("/jogos", methods=["POST"])
def adicionar_jogo():
    data = request.json
    nome = data.get("nome")
    nota = data.get("nota")
    status = data.get("status")
    comentario = data.get("comentario")

    if not nome:
        return jsonify({"erro": "Nome do jogo é obrigatório."}), 400

    resultado = igdb.buscar_jogos(nome)
    if not resultado:
        return jsonify({"erro": "Jogo não encontrado na IGDB."}), 404

    info = resultado[0]
    capa_id = info.get("cover", {}).get("image_id") if "cover" in info else None

    jogo = Jogo(
        id_igdb=info["id"],
        nome=info["name"],
        resumo=info.get("summary"),
        data_lancamento=info.get("first_release_date"),
        generos=', '.join([g["name"] for g in info.get("genres", [])]) if "genres" in info else '',
        plataformas=', '.join([p["name"] for p in info.get("platforms", [])]) if "platforms" in info else '',
        nota=nota,
        status=status or "quero jogar",
        comentario=comentario or "",
        capa_id=capa_id,
        usuario_id=1
    )

    db = sqlite3.connect("steamboxd.db")
    jogo.salvar(db)
    db.close()

    return jsonify({"mensagem": f"Jogo '{jogo.nome}' salvo com sucesso!"}), 201

@app.route("/jogos", methods=["GET"])
def listar_jogos():
    db = sqlite3.connect("steamboxd.db")
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, nome, nota, status, comentario, resumo, plataformas, generos, data_lancamento, capa_id
        FROM jogos
    """)
    dados = cursor.fetchall()
    db.close()

    jogos = []
    for r in dados:
        jogos.append({
            "id": r[0],
            "nome": r[1],
            "nota": r[2],
            "status": r[3],
            "comentario": r[4],
            "resumo": r[5],
            "plataformas": r[6],
            "generos": r[7],
            "data_lancamento": r[8],
            "capa_id": r[9]
        })

    return jsonify(jogos)

# Remove jogo do banco
@app.route("/jogos/<nome>", methods=["DELETE"])
def remover_jogo(nome):
    db = sqlite3.connect("steamboxd.db")
    cursor = db.cursor()
    cursor.execute("DELETE FROM jogos WHERE nome = ?", (nome,))
    db.commit()
    db.close()
    return jsonify({"mensagem": f"Jogo '{nome}' removido com sucesso."})

# Edita nota, status e comentário
@app.route("/jogos/<nome>", methods=["PUT"])
def editar_jogo(nome):
    data = request.json
    nota = data.get("nota")
    status = data.get("status")
    comentario = data.get("comentario")

    db = sqlite3.connect("steamboxd.db")
    cursor = db.cursor()
    cursor.execute("""
        UPDATE jogos
        SET nota = ?, status = ?, comentario = ?
        WHERE nome = ?
    """, (nota, status, comentario, nome))
    db.commit()
    db.close()

    return jsonify({"mensagem": f"Jogo '{nome}' atualizado com sucesso."})

if __name__ == "__main__":
    app.run(debug=True)
