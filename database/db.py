import os
import sqlite3

# Suporte a PostgreSQL (Produção/Vercel) ou SQLite (Local)
DATABASE_URL = os.environ.get("DATABASE_URL")

SCHEMA = """
CREATE TABLE IF NOT EXISTS pratos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL,
    popularidade_score REAL DEFAULT 0.5
);

CREATE TABLE IF NOT EXISTS cardapio (
    id INTEGER PRIMARY KEY,
    data TEXT NOT NULL,
    prato_id INTEGER,
    FOREIGN KEY (prato_id) REFERENCES pratos(id)
);

CREATE TABLE IF NOT EXISTS producao (
    id INTEGER PRIMARY KEY,
    data TEXT NOT NULL,
    prato_id INTEGER,
    quantidade_produzida INTEGER,
    quantidade_consumida INTEGER,
    sobra INTEGER,
    FOREIGN KEY (prato_id) REFERENCES pratos(id)
);

CREATE TABLE IF NOT EXISTS previsao (
    id INTEGER PRIMARY KEY,
    data TEXT NOT NULL,
    prato_id INTEGER,
    quantidade_prevista INTEGER,
    tipo TEXT DEFAULT 'auto',
    FOREIGN KEY (prato_id) REFERENCES pratos(id)
);

CREATE TABLE IF NOT EXISTS relatorios (
    id INTEGER PRIMARY KEY,
    data TEXT NOT NULL,
    tipo TEXT NOT NULL,
    conteudo TEXT NOT NULL
);
"""

def get_conn():
    if DATABASE_URL:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        # Adiciona suporte a dicionário para manter compatibilidade com Row do SQLite
        return conn
    else:
        DB_PATH = os.path.join(os.path.dirname(__file__), "marmitas.db")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_conn()
    if DATABASE_URL:
        # PostgreSQL não aceita executescript diretamente
        with conn.cursor() as cur:
            # Substitui SERIAL no Postgres se preferir, mas INTEGER PRIMARY KEY funciona em alguns contextos
            # Vamos ajustar o SCHEMA para Postgres na execução se necessário
            pg_schema = SCHEMA.replace("INTEGER PRIMARY KEY", "SERIAL PRIMARY KEY").replace("TEXT", "VARCHAR(255)")
            for statement in pg_schema.split(";"):
                if statement.strip():
                    cur.execute(statement)
        conn.commit()
    else:
        conn.executescript(SCHEMA)
        try:
            conn.execute("ALTER TABLE previsao ADD COLUMN tipo TEXT DEFAULT 'auto'")
        except:
            pass
        conn.commit()
    conn.close()

def query(sql, params=()):
    conn = get_conn()
    if DATABASE_URL:
        from psycopg2.extras import RealDictCursor
        # Converte '?' para '%s' para compatibilidade Postgres
        sql = sql.replace("?", "%s")
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = [dict(r) for r in cur.fetchall()]
    else:
        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    conn.close()
    return rows

def execute(sql, params=()):
    conn = get_conn()
    if DATABASE_URL:
        sql = sql.replace("?", "%s")
        with conn.cursor() as cur:
            cur.execute(sql, params)
            last_id = None # Postgres precisa de RETURNING para last_id
        conn.commit()
        last_id = 0 # Dummy
    else:
        cur = conn.execute(sql, params)
        conn.commit()
        last_id = cur.lastrowid
    conn.close()
    return last_id
