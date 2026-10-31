import json
import sqlite3
import glob

# Localiza o backup e o banco de dados
json_files = glob.glob("../*.json") + glob.glob("*.json")
db_files = glob.glob("*.db")

if not json_files or not db_files:
    print("Erro: Arquivo de backup ou banco de dados não encontrado!")
    input("Pressione Enter para sair...")
    exit()

print(f"Lendo backup: {json_files[0]}")
with open(json_files[0], "r", encoding="utf-8") as f:
    data = json.load(f)

conn = sqlite3.connect(db_files[0])
cursor = conn.cursor()

print("Limpando tabelas oficiais de parâmetros e setups...")
# Remove tabelas ou dados antigos que geram conflito
cursor.execute("DROP TABLE IF EXISTS parametros;")
cursor.execute("DROP TABLE IF EXISTS setups;")

# Recria a tabela de parâmetros oficial no formato correto
cursor.execute("""
    CREATE TABLE IF NOT EXISTS parametros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categoria TEXT,
        nome TEXT,
        descricao TEXT
    )
""")

print("Extraindo os setups e parâmetros reais do backup...")
# Varre o JSON procurando chaves que contenham os cadastros
for key, value in data.items():
    # Se a chave for de parâmetros ou setups, ou se o valor for uma lista de dicionários com 'nome'/'descricao'
    if "setup" in key.lower() or "param" in key.lower() or isinstance(value, list):
        items = value if isinstance(value, list) else [value]
        for item in items:
            if isinstance(item, dict):
                nome = item.get("nome") or item.get("titulo") or item.get("item")
                descricao = item.get("descricao") or item.get("regra") or item.get("possibilidades", "")
                if nome:
                    cursor.execute(
                        "INSERT INTO parametros (categoria, nome, descricao) VALUES (?, ?, ?)",
                        (key, str(nome), str(descricao))
                    )

conn.commit()
conn.close()
print("\n[SUCESSO] Setups e parâmetros extraídos do backup e gravados no banco oficial!")
input("Pressione Enter para fechar...")