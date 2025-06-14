from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import sqlite3
from api import IGDBClient
from database import criar_banco
from models.jogo import Jogo
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__, static_folder="../frontend")
app.secret_key = "chave-secreta-supersegura"
CORS(app, supports_credentials=True)

criar_banco()

CLIENT_ID = "j39kwre2g3ed7doj858xjwaex7yjz5"
CLIENT_SECRET = "krpia7k46sqpg2tu9c2cn23qnny6sm"
igdb = IGDBClient(CLIENT_ID, CLIENT_SECRET)

@app.route("/registrar", methods=["POST"])
def registrar():
    data = request.json
    nome = data.get("nome")
    email = data.get("email")
    senha = data.get("senha")

    senha_hash = generate_password_hash(senha)
    db = sqlite3.connect("steamboxd.db")
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)", (nome, email, senha_hash))
        db.commit()
        return jsonify({"mensagem": "Usuário registrado com sucesso!"})
    except sqlite3.IntegrityError:
        return jsonify({"erro": "Email já cadastrado."}), 400
    finally:
        db.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    senha = data.get("senha")

    db = sqlite3.connect("steamboxd.db")
    cursor = db.cursor()
    cursor.execute("SELECT id, nome, senha_hash FROM usuarios WHERE email = ?", (email,))
    usuario = cursor.fetchone()
    db.close()

    if usuario and check_password_hash(usuario[2], senha):
        session["usuario_id"] = usuario[0]
        session.permanent = True
        return jsonify({"mensagem": f"Bem-vindo, {usuario[1]}!"})
    return jsonify({"erro": "Credenciais inválidas"}), 401

@app.route("/logout")
def logout():
    session.pop("usuario_id", None)
    return jsonify({"mensagem": "Deslogado com sucesso"})

@app.route("/usuario-logado")
def usuario_logado():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return jsonify({"logado": False})

    db = sqlite3.connect("steamboxd.db")
    cursor = db.cursor()
    cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (usuario_id,))
    usuario = cursor.fetchone()
    db.close()

    if usuario:
        return jsonify({"logado": True, "nome": usuario[0]})
    return jsonify({"logado": False})

@app.route("/jogos", methods=["POST"])
def adicionar_jogo():
    if "usuario_id" not in session:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    data = request.json
    nome = data.get("nome")
    nota = data.get("nota")
    status = data.get("status")
    comentario = data.get("comentario")
    favorito = int(bool(data.get("favorito", 0)))

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
        favorito=favorito,
        usuario_id=session["usuario_id"]
    )

    db = sqlite3.connect("steamboxd.db")
    jogo.salvar(db)
    db.close()

    return jsonify({"mensagem": f"Jogo '{jogo.nome}' salvo com sucesso!"}), 201

@app.route("/jogos", methods=["GET"])
def listar_jogos():
    if "usuario_id" not in session:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    db = sqlite3.connect("steamboxd.db")
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, nome, nota, status, comentario, resumo, plataformas, generos, data_lancamento, capa_id, favorito
        FROM jogos
        WHERE usuario_id = ?
    """, (session["usuario_id"],))
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
            "capa_id": r[9],
            "favorito": bool(r[10])
        })

    return jsonify(jogos)

@app.route("/jogos/<nome>", methods=["DELETE"])
def remover_jogo(nome):
    if "usuario_id" not in session:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    db = sqlite3.connect("steamboxd.db")
    cursor = db.cursor()
    cursor.execute("DELETE FROM jogos WHERE nome = ? AND usuario_id = ?", (nome, session["usuario_id"]))
    db.commit()
    db.close()
    return jsonify({"mensagem": f"Jogo '{nome}' removido com sucesso."})

@app.route("/jogos/<nome>", methods=["PUT"])
def editar_jogo(nome):
    if "usuario_id" not in session:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    data = request.json
    nota = data.get("nota")
    status = data.get("status")
    comentario = data.get("comentario")

    db = sqlite3.connect("steamboxd.db")
    cursor = db.cursor()
    cursor.execute("""
        UPDATE jogos
        SET nota = ?, status = ?, comentario = ?
        WHERE nome = ? AND usuario_id = ?
    """, (nota, status, comentario, nome, session["usuario_id"]))
    db.commit()
    db.close()

    return jsonify({"mensagem": f"Jogo '{nome}' atualizado com sucesso."})

@app.route("/jogos/favorito/<nome>", methods=["PUT"])
def atualizar_favorito(nome):
    if "usuario_id" not in session:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    data = request.json
    favorito = data.get("favorito", 0)

    db = sqlite3.connect("steamboxd.db")
    cursor = db.cursor()
    cursor.execute("""
        UPDATE jogos
        SET favorito = ?
        WHERE nome = ? AND usuario_id = ?
    """, (favorito, nome, session["usuario_id"]))
    db.commit()
    db.close()

    return jsonify({"mensagem": f"Favorito atualizado para {bool(favorito)}."})

@app.route("/")
def login_html():
    return send_from_directory(app.static_folder, "login.html")

@app.route("/index.html")
def index_html():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/login.html")
def login_html_alias():
    return send_from_directory(app.static_folder, "login.html")

if __name__ == "__main__":
    app.run(debug=True)
