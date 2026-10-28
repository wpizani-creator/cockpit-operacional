import sqlite3
import os

DB_PATH = "trades.db"

def migrar_banco():
    if not os.path.exists(DB_PATH):
        print("Arquivo trades.db não encontrado!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Verifica as colunas atuais da tabela trades
    cursor.execute("PRAGMA table_info(trades)")
    colunas_existentes = [col[1] for col in cursor.fetchall()]

    novas_colunas = ["opcao1", "opcao2", "opcao3"]

    for col in novas_colunas:
        if col not in colunas_existentes:
            print(f"Adicionando coluna '{col}' ao banco de dados...")
            cursor.execute(f"ALTER TABLE trades ADD COLUMN {col} TEXT DEFAULT ''")

    conn.commit()
    conn.close()
    print("Migração concluída com sucesso! Seus dados e notas foram preservados.")

if __name__ == "__main__":
    migrar_banco()