import sqlite3

db = sqlite3.connect("steamboxd.db")
cursor = db.cursor()

cursor.execute("SELECT * FROM jogos")
jogos = cursor.fetchall()

for jogo in jogos:
    print(jogo)

db.close()