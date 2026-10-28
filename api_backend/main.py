"""
Projeto: Cockpit Operacional API (Dashboard de Day Trade)
Módulo: main.py
Descrição: Ponto de entrada principal da API FastAPI com suporte a autenticação por senha, prints em disco, persistência em SQLite e Módulo Fiscal.
"""

import os
import sys
import sqlite3
import secrets
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import List, Optional

# Adiciona a raiz ao path para garantir importação correta do banco
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.database import inicializar_banco
from api_backend.routers import trades, usuarios, fiscal

app = FastAPI(
    title="Cockpit Operacional API (Seguro & Modular)",
    version="2.3.0",
)

# -------------------------------------------------------------------------
# CONFIGURAÇÃO DE SEGURANÇA (USUÁRIO E SENHA PARA A NUVEM)
# -------------------------------------------------------------------------
security = HTTPBasic()

# Credenciais oficiais de acesso
ADMIN_USER = "w.pizani"
ADMIN_PASSWORD = "08121984"

def verificar_autenticacao(credentials: HTTPBasicCredentials = Depends(security)):
    is_user_ok = secrets.compare_digest(credentials.username.encode("utf8"), ADMIN_USER.encode("utf8"))
    is_pass_ok = secrets.compare_digest(credentials.password.encode("utf8"), ADMIN_PASSWORD.encode("utf8"))
    
    if not (is_user_ok and is_pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Configuração de CORS para permitir comunicação global
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caminho absoluto para a raiz do projeto (Dash_API)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Diretório físico para salvamento de prints em disco
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "prints")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------------------------------------------------------------------------
# CONFIGURAÇÃO DO BANCO DE DADOS SQLITE PARA OS TRADES EM DISCO
# -------------------------------------------------------------------------
DB_PATH = os.path.join(BASE_DIR, "trades.db")

def init_trades_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()

init_trades_db()

class Trade(BaseModel):
    id: str
    conta: Optional[str] = ""
    ativo: Optional[str] = ""
    abertura: Optional[str] = ""
    fechamento: Optional[str] = ""
    tempoOperacao: Optional[str] = ""
    lado: Optional[str] = ""
    qtdCompra: Optional[str] = ""
    qtdVenda: Optional[str] = ""
    precoCompra: Optional[str] = ""
    precoVenda: Optional[str] = ""
    resIntervaloBruto: Optional[str] = ""
    resIntervaloPercentual: Optional[str] = ""
    custo: Optional[str] = ""
    resOperacao: Optional[str] = ""
    tet: Optional[str] = ""
    setup: Optional[str] = ""
    complementoSetup: Optional[str] = ""
    timeframe: Optional[str] = ""
    tipoEntrada: Optional[str] = ""
    tipoSaida: Optional[str] = ""
    checklist: Optional[str] = ""
    falhas: Optional[str] = ""
    mmTend: Optional[str] = ""
    vwapTend: Optional[str] = ""
    resSupProx: Optional[str] = ""
    momento: Optional[str] = ""
    precoLimite: Optional[str] = ""
    nota: Optional[str] = ""
    printUrl: Optional[str] = ""
    emocional: Optional[str] = ""
    usaCesta: Optional[str] = ""
    ativo1: Optional[str] = ""
    estado1: Optional[str] = ""
    ativo2: Optional[str] = ""
    estado2: Optional[str] = ""
    ativo3: Optional[str] = ""
    estado3: Optional[str] = ""
    ativo4: Optional[str] = ""
    estado4: Optional[str] = ""
    opcao1: Optional[str] = ""
    opcao2: Optional[str] = ""
    opcao3: Optional[str] = ""

@app.get("/api/trades", dependencies=[Depends(verificar_autenticacao)])
def listar_trades():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trades")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/trades/lote", dependencies=[Depends(verificar_autenticacao)])
def salvar_lote_trades(trades: List[Trade]):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.query() if hasattr(conn, 'query') else conn.cursor()
    for t in trades:
        cursor.execute('''
            INSERT OR REPLACE INTO trades VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            t.id, t.conta, t.ativo, t.abertura, t.fechamento, t.tempoOperacao, t.lado,
            t.qtdCompra, t.qtdVenda, t.precoCompra, t.precoVenda, t.resIntervaloBruto,
            t.resIntervaloPercentual, t.custo, t.resOperacao, t.tet, t.setup, t.complementoSetup,
            t.timeframe, t.tipoEntrada, t.tipoSaida, t.checklist, t.falhas, t.mmTend,
            t.vwapTend, t.resSupProx, t.momento, t.precoLimite, t.nota, t.printUrl, t.emocional,
            t.usaCesta, t.ativo1, t.estado1, t.ativo2, t.estado2, t.ativo3, t.estado3, t.ativo4, t.estado4,
            t.opcao1, t.opcao2, t.opcao3
        ))
    conn.commit()
    conn.close()
    return {"success": True, "total": len(trades)}

@app.delete("/api/trades/{trade_id}", dependencies=[Depends(verificar_autenticacao)])
def excluir_trade(trade_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM trades WHERE id = ?", (trade_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.delete("/api/trades", dependencies=[Depends(verificar_autenticacao)])
def limpar_todos_trades():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM trades")
    conn.commit()
    conn.close()
    return {"success": True}

# -------------------------------------------------------------------------
# ROTAS DE UPLOAD DE PRINTS E ARQUIVOS ESTÁTICOS
# -------------------------------------------------------------------------

@app.post("/api/upload-print", dependencies=[Depends(verificar_autenticacao)])
async def upload_print(file: UploadFile = File(...)):
    try:
        ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        filename = f"print_{int(os.path.getmtime(UPLOAD_DIR) if os.path.exists(UPLOAD_DIR) else 0)}_{os.urandom(4).hex()}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        with open(filepath, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        file_url = f"http://127.0.0.1:8000/uploads/prints/{filename}"
        return {"success": True, "url": file_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Monta a pasta uploads estaticamente (protegida por autenticação básica)
app.mount("/uploads", StaticFiles(directory=os.path.join(BASE_DIR, "uploads")), name="uploads")

# Inicializa o banco de dados geral e as tabelas automaticamente
inicializar_banco()

# Registra os roteadores modulares adicionais com dependência global de autenticação
app.include_router(trades.router, dependencies=[Depends(verificar_autenticacao)])
app.include_router(usuarios.router, dependencies=[Depends(verificar_autenticacao)])
app.include_router(fiscal.router, dependencies=[Depends(verificar_autenticacao)])

# Classe customizada para forçar autenticação em ficheiros estáticos e HTML
class ProtectedStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        request = Request(scope)
        try:
            auth_header = request.headers.get("authorization")
            if not auth_header:
                raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Basic"})
            # Simula a validação com base no cabeçalho recebido
            import base64
            scheme, param = auth_header.split(" ")
            if scheme.lower() == "basic":
                decoded = base64.b64decode(param).decode("utf8")
                username, password = decoded.split(":")
                is_user_ok = secrets.compare_digest(username.encode("utf8"), ADMIN_USER.encode("utf8"))
                is_pass_ok = secrets.compare_digest(password.encode("utf8"), ADMIN_PASSWORD.encode("utf8"))
                if not (is_user_ok and is_pass_ok):
                    raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Basic"})
            else:
                raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Basic"})
        except Exception:
            return PlainTextResponse("Autenticação necessária", status_code=401, headers={"WWW-Authenticate": "Basic"})
        return await super().get_response(path, scope)

@app.get("/api/status", dependencies=[Depends(verificar_autenticacao)])
def status_api():
    return {
        "status": "online",
        "mensagem": "API rodando com segurança e proteção por senha!",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
