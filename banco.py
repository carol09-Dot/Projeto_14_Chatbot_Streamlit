
import sqlite3


# Conectar ao banco de dados
def conectar():
    return sqlite3.connect("catbot.db")


# Criar as tabelas do banco
def criar_tabelas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL DEFAULT 'Nova conversa',
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversa_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversa_id) REFERENCES conversas(id)
        )
    """)

    conexao.commit()
    conexao.close()


# Criar uma nova conversa
def criar_conversa(titulo="Nova conversa"):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "INSERT INTO conversas (titulo) VALUES (?)",
        (titulo,)
    )

    conversa_id = cursor.lastrowid

    conexao.commit()
    conexao.close()

    return conversa_id


# Salvar uma mensagem
def salvar_mensagem(conversa_id, role, conteudo):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO mensagens (conversa_id, role, conteudo)
        VALUES (?, ?, ?)
        """,
        (conversa_id, role, conteudo)
    )

    conexao.commit()
    conexao.close()


# Buscar as conversas salvas
def listar_conversas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, titulo, data_criacao
        FROM conversas
        ORDER BY id DESC
    """)

    conversas = cursor.fetchall()
    conexao.close()

    return conversas


# Buscar as mensagens de uma conversa
def buscar_mensagens(conversa_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT role, conteudo
        FROM mensagens
        WHERE conversa_id = ?
        ORDER BY id ASC
    """, (conversa_id,))

    mensagens = cursor.fetchall()
    conexao.close()

    return [
        {"role": role, "content": conteudo}
        for role, conteudo in mensagens
    ]


# Atualizar o título de uma conversa
def atualizar_titulo(conversa_id, titulo):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "UPDATE conversas SET titulo = ? WHERE id = ?",
        (titulo, conversa_id)
    )

    conexao.commit()
    conexao.close()
