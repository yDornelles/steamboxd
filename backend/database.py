import sqlite3

def criar_banco():
    db = sqlite3.connect("steamboxd.db")
    cursor = db.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_igdb INTEGER,
            nome TEXT NOT NULL,
            resumo TEXT,
            data_lancamento INTEGER,
            generos TEXT,
            plataformas TEXT,
            nota INTEGER,
            status TEXT,
            comentario TEXT,
            capa_id TEXT,
            usuario_id INTEGER,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    ''')

    db.commit()
    db.close()
