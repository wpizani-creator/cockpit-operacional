"""
Projeto: Cockpit Operacional API (Dashboard de Day Trade)
Módulo: routers/trades.py
Descrição: Endpoints de listagem, cadastro e resumo estatístico de operações.
Autor: Especialista / Analista Day Trade
Data: 2026-08-28
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os

# Adiciona o diretório raiz ao caminho para importar o banco de dados
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from database.database import conectar

router = APIRouter(
    prefix="/trades",
    tags=["Trades"]
)

class TradeSchema(BaseModel):
    data_abertura: str
    hora_abertura: str
    data_encerramento: str
    hora_encerramento: str
    codigo: str
    lado: str
    qtd_compra: int
    qtd_venda: int
    preco_compra: float
    preco_vendido: float
    resultado_bruto: float
    corretagem: float
    taxas: float
    resultado_liquido: float
    setup: str
    observacoes: str = ""

@router.get("/")
def listar_trades():
    """Retorna todas as operações cadastradas no banco de dados isolado."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trades")
    linhas = cursor.fetchall()
    conn.close()
    
    trades_lista = [dict(linha) for linha in linhas]
    return {
        "total": len(trades_lista),
        "trades": trades_lista
    }

@router.get("/resumo")
def resumo_trades():
    """Retorna um resumo estatístico consolidado de todos os trades cadastrados."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trades")
    linhas = cursor.fetchall()
    conn.close()
    
    trades = [dict(linha) for linha in linhas]
    total_trades = len(trades)
    
    if total_trades == 0:
        return {"total_trades": 0, "resultado_liquido_total": 0.0, "taxa_acerto_pct": 0.0}
    
    resultado_total = sum(t["resultado_liquido"] for t in trades)
    vencedores = sum(1 for t in trades if t["resultado_liquido"] > 0)
    taxa_acerto = (vencedores / total_trades) * 100
    
    return {
        "total_trades": total_trades,
        "resultado_liquido_total": round(resultado_total, 2),
        "trades_vencedores": vencedores,
        "trades_perdedores": total_trades - vencedores,
        "taxa_acerto_pct": round(taxa_acerto, 2)
    }

@router.post("/")
def cadastrar_trade(trade: TradeSchema):
    """Cadastra uma nova operação de trade no banco de dados isolado."""
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO trades (
                data_abertura, hora_abertura, data_encerramento, hora_encerramento,
                codigo, lado, qtd_compra, qtd_venda, preco_compra, preco_vendido,
                resultado_bruto, corretagem, taxas, resultado_liquido, setup, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade.data_abertura, trade.hora_abertura, trade.data_encerramento, trade.hora_encerramento,
            trade.codigo, trade.lado, trade.qtd_compra, trade.qtd_venda, trade.preco_compra, trade.preco_vendido,
            trade.resultado_bruto, trade.corretagem, trade.taxas, trade.resultado_liquido, trade.setup, trade.observacoes
        ))
        
        conn.commit()
        trade_id = cursor.lastrowid
        conn.close()
        
        return {
            "sucesso": True,
            "mensagem": "Trade cadastrado com sucesso!",
            "id_inserido": trade_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))