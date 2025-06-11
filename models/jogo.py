class Jogo:    
    def __init__(self, id_igdb, nome, resumo=None, data_lancamento=None, generos=None, plataformas=None, nota=None, status=None, comentario=None, usuario_id=None):
        self.id_igdb = id_igdb
        self.nome = nome
        self.resumo = resumo
        self.data_lancamento = data_lancamento
        self.generos = generos or ""
        self.plataformas = plataformas or ""
        self.nota = nota
        self.status = status
        self.comentario = comentario
        self.usuario_id = usuario_id

    def salvar(self, db):
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO jogos (id_igdb, nome, resumo, data_lancamento, generos, plataformas, nota, status, comentario, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.id_igdb,
            self.nome,
            self.resumo,
            self.data_lancamento,
            self.generos,
            self.plataformas,
            self.nota,
            self.status,
            self.comentario,
            self.usuario_id
        ))
        db.commit()
