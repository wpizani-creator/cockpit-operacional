"""
Projeto: Cockpit Operacional API (Dashboard de Day Trade)
Módulo: fiscal.py
Descrição: Módulo Fiscal PRO - Processamento de PDFs e gestão unificada de Histórico de Prejuízos (Importados + Manuais).
Utilizando o modelo oficial atualizado: gemini-3.8-flash.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import os
import shutil
import json
import re
import time
from typing import Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

router = APIRouter(prefix="/api/fiscal", tags=["Fiscal & IR"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDF_UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "notas_fiscais")
DB_DIR = os.path.join(BASE_DIR, "database")
DB_FILE = os.path.join(DB_DIR, "notas_fiscais_db.json")
PREJUIZOS_DB_FILE = os.path.join(DB_DIR, "prejuizos_manuais_db.json")

os.makedirs(PDF_UPLOAD_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

if not os.path.exists(PREJUIZOS_DB_FILE):
    with open(PREJUIZOS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

def ler_historico_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def salvar_historico_db(dados):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def ler_prejuizos_db():
    try:
        with open(PREJUIZOS_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def salvar_prejuizos_db(dados):
    with open(PREJUIZOS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

class ToggleRequest(BaseModel):
    index: int

class MarcarTodasRequest(BaseModel):
    status: bool

class PrejuizoManualModel(BaseModel):
    mes_ano: str # Formato "YYYY-MM"
    valor: float # Valor negativo do prejuízo ou absoluto
    observacao: Optional[str] = ""

class DeletarPrejuizoRequest(BaseModel):
    id: str

@router.get("/historico")
async def obter_historico():
    return {"success": True, "historico": ler_historico_db()}

@router.post("/limpar-historico")
async def limpar_historico():
    salvar_historico_db([])
    return {"success": True, "message": "Histórico limpo com sucesso."}

@router.post("/toggle-arquivo")
async def toggle_arquivo(req: ToggleRequest):
    historico = ler_historico_db()
    if 0 <= req.index < len(historico):
        atual = historico[req.index].get("selecionado", True)
        historico[req.index]["selecionado"] = not atual
        salvar_historico_db(historico)
        return {"success": True, "selecionado": historico[req.index]["selecionado"]}
    raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

@router.post("/marcar-todas")
async def marcar_todas(req: MarcarTodasRequest):
    historico = ler_historico_db()
    for item in historico:
        item["selecionado"] = req.status
    salvar_historico_db(historico)
    return {"success": True, "status": req.status}

# ROTA DE GESTÃO DE PREJUÍZOS MANUAIS
@router.get("/prejuizos-manuais")
async def obter_prejuizos_manuais():
    return {"success": True, "prejuizos": ler_prejuizos_db()}

@router.post("/salvar-prejuizo-manual")
async def salvar_prejuizo_manual(req: PrejuizoManualModel):
    prejuizos = ler_prejuizos_db()
    valor_prejuizo = -abs(req.valor)

    encontrado = False
    for item in prejuizos:
        if item.get("mes_ano") == req.mes_ano:
            item["valor"] = valor_prejuizo
            item["observacao"] = req.observacao
            encontrado = True
            break
            
    if not encontrado:
        novo_id = f"man_{len(prejuizos) + 1}_{req.mes_ano}"
        prejuizos.append({
            "id": novo_id,
            "mes_ano": req.mes_ano,
            "valor": valor_prejuizo,
            "observacao": req.observacao,
            "tipo": "manual"
        })
        
    salvar_prejuizos_db(prejuizos)
    return {"success": True, "prejuizos": prejuizos}

@router.post("/deletar-prejuizo-manual")
async def deletar_prejuizo_manual(req: DeletarPrejuizoRequest):
    prejuizos = ler_prejuizos_db()
    prejuizos = [p for p in prejuizos if p.get("id") != req.id]
    salvar_prejuizos_db(prejuizos)
    return {"success": True, "prejuizos": prejuizos}

@router.post("/processar-pdf")
async def processar_pdf_nota(file: UploadFile = File(...)):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or "sua_chave_aqui" in api_key:
            raise HTTPException(
                status_code=400, 
                detail="Chave da API do Gemini (GEMINI_API_KEY) não foi configurada no arquivo .env."
            )

        client = genai.Client(api_key=api_key)

        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Apenas arquivos PDF são permitidos.")
        
        filepath = os.path.join(PDF_UPLOAD_DIR, file.filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        arquivo_gemini = client.files.upload(file=filepath)

        prompt_extracao = """
        Você é um especialista contábil em mercado financeiro brasileiro.
        Analise esta Nota de Corretagem / Extrato da Genial Investimentos (B3 / BM&F) e extraia TODAS as notas de corretagem diárias presentes neste documento.

        Para cada nota de corretagem diária encontrada, extraia exatamente os seguintes campos:
        - data: Data do pregão no formato DD/MM/AAAA.
        - nota: Número da nota de corretagem (Nr. nota).
        - corretora: Corretora e código (ex: "Genial / 1885259").
        - mercado: Mercado operado (ex: "BM&F (WIN/WDO)" ou "B3 (Ações)").
        - valor_negocios: Valor do campo 'Valor dos negócios' ou 'Ajuste day trade' (float). Se for Débito (D), negativo; Crédito (C), positivo.
        - total_despesas: Valor do campo 'Total das despesas' (float). Sempre um número positivo referente aos custos totais da nota.
        - irrf: Valor do campo 'IRRF Day Trade (Projeção)' ou 'IRRF' retido na fonte (float).
        - liquido: Valor do 'Total liquido da nota' ou 'Total líquido' (float). Débito (D) = NEGATIVO, Crédito (C) = POSITIVO.

        Responda ESTRITAMENTE em formato JSON puro, sem textos adicionais, com a seguinte estrutura exata:
        {
          "qtd_notas": 1,
          "irrf_total": 0.0,
          "notas": [
            {
              "data": "11/11/2025",
              "nota": "712416",
              "corretora": "Genial / 1885259",
              "mercado": "BM&F (WIN/WDO)",
              "valor_negocios": 33.00,
              "total_despesas": 4.00,
              "irrf": 0.29,
              "liquido": 28.71
            }
          ]
        }
        """

        # Chamada utilizando estritamente o modelo correto gemini-3.8-flash com retentativa
        resposta = None
        erro_ultimo = None

        for tentativa in range(3):
            try:
                resposta = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=[arquivo_gemini, prompt_extracao],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                if resposta and resposta.text:
                    break
            except Exception as err:
                erro_ultimo = err
                print(f"Tentativa {tentativa+1} com gemini-3.8-flash falhou: {str(err)}. Aguardando 2s...")
                time.sleep(2)

        try:
            client.files.delete(name=arquivo_gemini.name)
        except Exception:
            pass

        if not resposta or not resposta.text:
            raise HTTPException(
                status_code=503, 
                detail=f"O servidor do Gemini está temporariamente indisponível. Erro: {str(erro_ultimo)}"
            )

        texto_limpo = resposta.text.strip()
        if texto_limpo.startswith("```"):
            texto_limpo = re.sub(r"^```[a-zA-Z]*\n?", "", texto_limpo)
            texto_limpo = re.sub(r"\n?```$", "", texto_limpo).strip()

        dados_extraidos = json.loads(texto_limpo)

        historico = ler_historico_db()
        
        for item in historico:
            item["selecionado"] = False

        novo_registro = {
            "id": len(historico) + 1,
            "nome": file.filename,
            "data": os.path.getctime(filepath) if os.path.exists(filepath) else 0,
            "selecionado": True,
            "notas": dados_extraidos.get("notas", [])
        }
        historico.append(novo_registro)
        salvar_historico_db(historico)

        return {
            "success": True,
            "filename": file.filename,
            "qtd_notas": dados_extraidos.get("qtd_notas", len(dados_extraidos.get("notas", []))),
            "irrf_total": dados_extraidos.get("irrf_total", 0.0),
            "notas": dados_extraidos.get("notas", [])
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Erro no processamento do PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar PDF: {str(e)}")