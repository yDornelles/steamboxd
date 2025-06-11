class Usuario:    
    def __init__(self, nome, email, senha):
        self.nome = nome
        self.email = email
        self.senha = senha

    def salvar(self, db):
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO usuarios (nome, email, senha)
            VALUES (?, ?, ?)
        ''', (self.nome, self.email, self.senha))
        db.commit()
