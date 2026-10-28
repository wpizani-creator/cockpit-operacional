"""
Módulo: database/database.py
Descrição: Gerencia a conexão com o SQLite e a criação das tabelas (Trades e Usuários).
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "cockpit.db")

def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()
    
    # Tabela de Trades (existente)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_abertura TEXT,
            hora_abertura TEXT,
            data_encerramento TEXT,
            hora_encerramento TEXT,
            codigo TEXT,
            lado TEXT,
            qtd_compra INTEGER,
            qtd_venda INTEGER,
            preco_compra REAL,
            preco_vendido REAL,
            resultado_bruto REAL,
            corretagem REAL,
            taxas REAL,
            resultado_liquido REAL,
            setup TEXT,
            observacoes TEXT
        )
    """)
    
    # Tabela de Usuários (nova para segurança)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            login TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            telefone TEXT NOT NULL,
            perfil TEXT NOT NULL,
            senha TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()