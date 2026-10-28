"""
Módulo: api_backend/routers/usuarios.py
Descrição: Endpoints de autenticação, cadastro e recuperação de senha de usuários.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os

# Adiciona a raiz ao path para importar o banco de dados
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from database.database import conectar

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

class UsuarioCreate(BaseModel):
    nome_completo: str
    login: str
    email: str
    telefone: str
    perfil: str
    senha: str

class LoginRequest(BaseModel):
    login: str
    senha: str

class VerificarRequest(BaseModel):
    email: str
    telefone: str

class AtualizarSenhaRequest(BaseModel):
    email: str
    nova_senha: str

@router.post("")
def cadastrar_usuario(user: UsuarioCreate):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO usuarios (nome_completo, login, email, telefone, perfil, senha)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user.nome_completo, user.login, user.email, user.telefone, user.perfil, user.senha))
        conn.commit()
        return {"mensagem": "Usuário cadastrado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao cadastrar usuário (Login ou E-mail já existem): {e}")
    finally:
        conn.close()

@router.post("/login")
def realizar_login(dados: LoginRequest):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE (login = ? OR email = ?) AND senha = ?", (dados.login, dados.login, dados.senha))
    usuario = cursor.fetchone()
    conn.close()
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")
    return {"mensagem": "Login bem-sucedido", "nome": usuario["nome_completo"], "perfil": usuario["perfil"]}

@router.post("/verificar")
def verificar_cadastro(dados: VerificarRequest):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ? AND telefone = ?", (dados.email, dados.telefone))
    usuario = cursor.fetchone()
    conn.close()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="E-mail ou telefone não encontrados.")
    return {"mensagem": "Usuário verificado com sucesso."}

@router.put("/atualizar-senha")
def atualizar_senha(dados: AtualizarSenhaRequest):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET senha = ? WHERE email = ?", (dados.nova_senha, dados.email))
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    
    if rows == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado para atualização.")
    return {"mensagem": "Senha atualizada com sucesso!"}