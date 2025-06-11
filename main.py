import sqlite3
from database import criar_banco
from models.jogo import Jogo
from api import IGDBClient

# Configurações
CLIENT_ID = 'j39kwre2g3ed7doj858xjwaex7yjz5'
CLIENT_SECRET = 'krpia7k46sqpg2tu9c2cn23qnny6sm'

# Inicialização
criar_banco()
db = sqlite3.connect("steamboxd.db")

# Criar cliente IGDB
igdb = IGDBClient(CLIENT_ID, CLIENT_SECRET)

# Buscar jogo
dados = igdb.buscar_jogos("The Witcher 3")

# Verificar resultado
if dados:
    info = dados[0]
    print(f"\nJogo encontrado: {info['name']}")

    # Perguntar dados ao usuário
    try:
        nota = float(input("\nDê uma nota para o jogo (0 a 10): "))
    except ValueError:
        nota = None

    status = input("Status (jogado, jogando, quero jogar, favorito...): ").strip()
    comentario = input("Comentário (opcional): ").strip()

    # Criar objeto Jogo
    jogo = Jogo(
        id_igdb=info['id'],
        nome=info['name'],
        resumo=info.get('summary'),
        data_lancamento=info.get('first_release_date'),
        generos=', '.join([g['name'] for g in info.get('genres', [])]) if 'genres' in info else '',
        plataformas=', '.join([p['name'] for p in info.get('platforms', [])]) if 'platforms' in info else '',
        nota=nota,
        status=status or "quero jogar",
        comentario=comentario,
        usuario_id=1 
    )

    jogo.salvar(db)
    print("\n✅ Jogo salvo no banco com sucesso!")
else:
    print("❌ Jogo não encontrado.")