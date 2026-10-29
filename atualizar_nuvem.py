"""
Script de Atualização Automática para a Nuvem
Objetivo: Executar git add, git commit e git push de forma automatizada.
"""

import os
import subprocess
from datetime import datetime

def executar_comando(comando):
    resultado = subprocess.run(comando, capture_output=True, text=True, shell=True)
    if resultado.returncode != 0:
        print(f"⚠️ Erro ao executar '{comando}': {resultado.stderr.strip()}")
        return False
    else:
        print(f"✅ Sucesso: {resultado.stdout.strip()}")
        return True

def atualizar_para_nuvem():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando atualização automática para a nuvem...")

    # 1. Adiciona todas as alterações e novos arquivos (prints, db, código)
    if not executar_comando("git add ."):
        return

    # 2. Cria o commit com data e hora automática
    mensagem_commit = f"Atualizacao automatizada via script - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    if not executar_comando(f'git commit -m "{mensagem_commit}"'):
        print("ℹ️ Nenhuma alteração nova para commitar.")
        return

    # 3. Envia para o repositório remoto (nuvem)
    if executar_comando("git push origin main"):
        print("🚀 Nuvem atualizada com sucesso!")
    else:
        print("❌ Falha ao enviar para o git push. Verifique sua conexão.")

if __name__ == "__main__":
    atualizar_para_nuvem()