"""
Projeto: Cockpit Operacional API (Dashboard de Day Trade)
Módulo: main.py
Descrição: Ponto de entrada principal da API FastAPI com tratamento de exceções blindado, suporte a autenticação, SQLite, rotas modulares e gerenciamento de metas.
"""

import os
import sys
import sqlite3
import secrets
import json
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status, Request, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

# Adiciona a raiz ao path para garantir importação correta do banco
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from database.database import inicializar_banco
except ImportError:
    def inicializar_banco():
        pass

try:
    from api_backend.routers import trades, usuarios, fiscal
except ImportError:
    trades = usuarios = fiscal = None

app = FastAPI(
    title="Cockpit Operacional API (Seguro & Modular)",
    version="2.5.2",
)

# -------------------------------------------------------------------------
# CONFIGURAÇÃO DE SEGURANÇA (USUÁRIO E SENHA)
# -------------------------------------------------------------------------
security = HTTPBasic()

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

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caminho absoluto para a raiz do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Diretório físico para salvamento de prints em disco
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "prints")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------------------------------------------------------------------------
# CONFIGURAÇÃO DO BANCO DE DADOS SQLITE
# -------------------------------------------------------------------------
DB_PATH = os.path.join(BASE_DIR, "trades.db")

def init_trades_db():
    try:
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

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parametros (
                chave TEXT PRIMARY KEY,
                valor TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contas (
                id TEXT PRIMARY KEY,
                valor TEXT
            )
        ''')

        conn.commit()
        conn.close()
    except Exception as e:
        print("Erro ao inicializar banco SQLite:", e)

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

# -------------------------------------------------------------------------
# ROTAS DE METAS (CORRIGIDO PARA ELIMINAR O ERRO 404)
# -------------------------------------------------------------------------
@app.get("/api/metas", dependencies=[Depends(verificar_autenticacao)])
def obter_metas():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'cockpit_metas'")
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0]:
            try:
                return json.loads(row[0])
            except:
                return {}
    except Exception:
        pass
    return {}

@app.post("/api/metas", dependencies=[Depends(verificar_autenticacao)])
async def salvar_metas(request: Request):
    try:
        dados = await request.json()
        valor_json = json.dumps(dados, ensure_ascii=False)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO configuracoes (chave, valor) VALUES ('cockpit_metas', ?)
            ON CONFLICT(chave) DO UPDATE SET valor = ?
        """, (valor_json, valor_json))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# -------------------------------------------------------------------------
# ROTAS DE PARÂMETROS CORRIGIDAS E BLINDADAS
# -------------------------------------------------------------------------
@app.get("/api/parametros", dependencies=[Depends(verificar_autenticacao)])
def listar_parametros(categoria: Optional[str] = Query(None)):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if categoria:
            chave_busca = f"cat_{categoria}"
            cursor.execute("SELECT valor FROM parametros WHERE chave = ?", (chave_busca,))
            row = cursor.fetchone()
            conn.close()
            if row and row["valor"]:
                try:
                    return json.loads(row["valor"])
                except:
                    return []
            return []
        
        cursor.execute("SELECT chave, valor FROM parametros")
        rows = cursor.fetchall()
        conn.close()
        
        resultado = {}
        for row in rows:
            try:
                resultado[row["chave"]] = json.loads(row["valor"])
            except:
                resultado[row["chave"]] = row["valor"]
        return resultado
    except Exception:
        return [] if categoria else {}

@app.post("/api/parametros", dependencies=[Depends(verificar_autenticacao)])
async def salvar_parametro(request: Request, categoria: Optional[str] = Query(None)):
    try:
        body_json = await request.json()
        if not categoria:
            categoria = "geral"

        chave_busca = f"cat_{categoria}"
        valor_str = json.dumps(body_json) if not isinstance(body_json, str) else body_json

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO parametros (chave, valor) VALUES (?, ?)", (chave_busca, valor_str))
        conn.commit()
        conn.close()
        return {"success": True, "categoria": categoria}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/parametros/lote", dependencies=[Depends(verificar_autenticacao)])
async def salvar_parametros_lote(request: Request):
    try:
        dados = await request.json()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for chave, valor in dados.items():
            chave_busca = f"cat_{chave}" if not chave.startswith("cat_") else chave
            valor_str = json.dumps(valor) if not isinstance(valor, str) else valor
            cursor.execute("INSERT OR REPLACE INTO parametros (chave, valor) VALUES (?, ?)", (chave_busca, valor_str))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# -------------------------------------------------------------------------
# ROTAS DE STATUS DARF
# -------------------------------------------------------------------------
@app.get("/api/fiscal/status-darf", dependencies=[Depends(verificar_autenticacao)])
def obter_status_darf():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'status_darf_map'")
        row = cursor.fetchone()
        conn.close()
        
        if row and row["valor"]:
            try:
                return json.loads(row["valor"])
            except:
                return {}
    except Exception:
        pass
    return {}

@app.post("/api/fiscal/status-darf", dependencies=[Depends(verificar_autenticacao)])
async def salvar_status_darf(request: Request):
    try:
        dados = await request.json()
        valor_json = json.dumps(dados)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO configuracoes (chave, valor) VALUES ('status_darf_map', ?)
            ON CONFLICT(chave) DO UPDATE SET valor = ?
        """, (valor_json, valor_json))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# -------------------------------------------------------------------------
# ROTAS DE CONTAS E TAXAS
# -------------------------------------------------------------------------
@app.get("/api/contas", dependencies=[Depends(verificar_autenticacao)])
def obter_contas():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'cockpit_contas_completo'")
        row = cursor.fetchone()
        conn.close()
        
        if row and row["valor"]:
            try:
                dados = json.loads(row["valor"])
                if isinstance(dados, list):
                    return dados
            except:
                pass
    except Exception as e:
        print("Erro ao obter contas:", e)
    return []

@app.post("/api/contas", dependencies=[Depends(verificar_autenticacao)])
async def salvar_contas(request: Request):
    try:
        novos_dados = await request.json()
        if not isinstance(novos_dados, list):
            novos_dados = [novos_dados] if novos_dados else []

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'cockpit_contas_completo'")
        row = cursor.fetchone()
        
        contas_existentes = []
        if row and row["valor"]:
            try:
                carregado = json.loads(row["valor"])
                if isinstance(carregado, list):
                    contas_existentes = carregado
            except:
                pass

        mapa_contas = {str(c.get("id", "")): c for c in contas_existentes if c.get("id")}
        
        for nova in novos_dados:
            nid = str(nova.get("id", "")).strip()
            if nid:
                if nid in mapa_contas:
                    mapa_contas[nid].update(nova)
                else:
                    mapa_contas[nid] = nova

        lista_final = list(mapa_contas.values())
        valor_json = json.dumps(lista_final, ensure_ascii=False)

        cursor.execute("""
            INSERT INTO configuracoes (chave, valor) VALUES ('cockpit_contas_completo', ?)
            ON CONFLICT(chave) DO UPDATE SET valor = ?
        """, (valor_json, valor_json))
        conn.commit()
        conn.close()
        
        return {"success": True, "total_salvo": len(lista_final)}
    except Exception as e:
        return {"success": False, "error": str(e)}

# -------------------------------------------------------------------------
# ROTAS DE TRADES
# -------------------------------------------------------------------------
@app.get("/api/trades", dependencies=[Depends(verificar_autenticacao)])
def listar_trades():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception:
        return []

@app.post("/api/trades/lote", dependencies=[Depends(verificar_autenticacao)])
def salvar_lote_trades(trades: List[Trade]):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
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
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.delete("/api/trades/{trade_id}", dependencies=[Depends(verificar_autenticacao)])
def excluir_trade(trade_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM trades WHERE id = ?", (trade_id,))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.delete("/api/trades", dependencies=[Depends(verificar_autenticacao)])
def limpar_todos_trades():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM trades")
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# -------------------------------------------------------------------------
# ROTAS DE UPLOAD DE PRINTS E ARQUIVOS ESTÁTICOS
# -------------------------------------------------------------------------
@app.post("/api/upload-print", dependencies=[Depends(verificar_autenticacao)])
async def upload_print(request: Request, file: UploadFile = File(...)):
    try:
        ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        filename = f"print_{int(os.path.getmtime(UPLOAD_DIR) if os.path.exists(UPLOAD_DIR) else 0)}_{os.urandom(4).hex()}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        with open(filepath, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        base_url = str(request.base_url).rstrip("/")
        file_url = f"{base_url}/uploads/prints/{filename}"
        return {"success": True, "url": file_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/uploads", StaticFiles(directory=os.path.join(BASE_DIR, "uploads")), name="uploads")

try:
    inicializar_banco()
except:
    pass

if trades and hasattr(trades, 'router'):
    app.include_router(trades.router, dependencies=[Depends(verificar_autenticacao)])
if usuarios and hasattr(usuarios, 'router'):
    app.include_router(usuarios.router, dependencies=[Depends(verificar_autenticacao)])
if fiscal and hasattr(fiscal, 'router'):
    app.include_router(fiscal.router, dependencies=[Depends(verificar_autenticacao)])

@app.get("/", dependencies=[Depends(verificar_autenticacao)])
def serve_root():
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Cockpit Operacional API ativa."}

frontend_path = os.path.join(BASE_DIR, "frontend")
if os.path.exists(frontend_path):
    app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

@app.get("/api/status", dependencies=[Depends(verificar_autenticacao)])
def status_api():
    return {
        "status": "online",
        "mensagem": "API rodando com tratamento de erros robusto no SQLite e rotas de metas integradas!",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)