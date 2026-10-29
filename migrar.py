"""
Projeto: Cockpit Operacional - Day Trade
Arquivo: migrar.py
Descrição: Script de migração de banco de dados SQLite (trades.db).
          Garante a existência das colunas da tabela trades e cria a tabela de parâmetros.
"""

import sqlite3
import os

# Define o caminho absoluto para o banco de dados na raiz do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "trades.db")

def migrar_banco():
    if not os.path.exists(DB_PATH):
        print(f"⚠️ Arquivo 'trades.db' não encontrado em: {DB_PATH}")
        print("Criando novo banco de dados SQLite...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🔄 Verificando e atualizando a estrutura do banco de dados SQLite...")

    # 1. Garante que a tabela trades existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id TEXT PRIMARY KEY,
            conta TEXT,
            ativo TEXT,
            abertura TEXT,
            fechamento TEXT,
            tempoOperacao TEXT,
            lado TEXT,
            qtdCompra TEXT,
            qtdVenda TEXT,
            precoCompra TEXT,
            precoVenda TEXT,
            resIntervaloBruto TEXT,
            resIntervaloPercentual TEXT,
            custo TEXT,
            resOperacao TEXT,
            tet TEXT,
            setup TEXT,
            complementoSetup TEXT,
            timeframe TEXT,
            tipoEntrada TEXT,
            tipoSaida TEXT,
            checklist TEXT,
            falhas TEXT,
            mmTend TEXT,
            vwapTend TEXT,
            resSupProx TEXT,
            momento TEXT,
            precoLimite TEXT,
            nota TEXT,
            printUrl TEXT,
            emocional TEXT,
            usaCesta TEXT,
            ativo1 TEXT,
            estado1 TEXT,
            ativo2 TEXT,
            estado2 TEXT,
            ativo3 TEXT,
            estado3 TEXT,
            ativo4 TEXT,
            estado4 TEXT,
            opcao1 TEXT,
            opcao2 TEXT,
            opcao3 TEXT
        )
    ''')

    # Verifica colunas existentes na tabela trades
    cursor.execute("PRAGMA table_info(trades)")
    colunas_existentes = [col[1] for col in cursor.fetchall()]

    novas_colunas = ["opcao1", "opcao2", "opcao3"]

    for col in novas_colunas:
        if col not in colunas_existentes:
            print(f"➕ Adicionando coluna '{col}' à tabela 'trades'...")
            cursor.execute(f"ALTER TABLE trades ADD COLUMN {col} TEXT DEFAULT ''")

    # 2. Garante a criação da tabela de parâmetros (Fase 1 / Migração localStorage)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parametros (
            chave TEXT PRIMARY KEY,
            valor TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Migração concluída com sucesso! Todos os dados de trades e parâmetros foram preservados.")

if __name__ == "__main__":
    migrar_banco()