class Jogo:
    def __init__(self, id_igdb, nome, resumo=None, data_lancamento=None,
                 generos=None, plataformas=None, nota=None, status="quero_jogar",
                 comentario=None, capa_id=None, usuario_id=None, favorito=False):
        self.id_igdb = id_igdb
        self.nome = nome
        self.resumo = resumo
        self.data_lancamento = data_lancamento
        self.generos = generos
        self.plataformas = plataformas
        self.nota = nota
        self.status = status
        self.comentario = comentario
        self.capa_id = capa_id
        self.usuario_id = usuario_id
        self.favorito = favorito

    def salvar(self, db):
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO jogos (
                id_igdb, nome, resumo, data_lancamento,
                generos, plataformas, nota, status,
                comentario, capa_id, usuario_id, favorito
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            self.capa_id,
            self.usuario_id,
            self.favorito 
        ))
        db.commit()
