import requests
import json

# Lista oficial extraída do seu backup com todos os 24 setups
setups_oficiais = [
    {"nome": "1º PIVOT ALINHADO MM20", "descricao": "PRIMEIRO PIVOT ALINHADO COM A MM20"},
    {"nome": "PULBACK OCULTO", "descricao": "PULBACK OCULTO"},
    {"nome": "STOP E REV FALHA PIVOT", "descricao": "STOP E REVERSÁO DA FALHA DO PIVOT"},
    {"nome": "PROFESSOR", "descricao": "TRADE ACOMPANHADO O PROFESSOR"},
    {"nome": "BREAKOUT PULBACK**", "descricao": "TRADE DE BREAKOUT - PB PÓS / PRÉ ROMP / ROMP - ESPECIFICAR NO COMPLEMENTO"},
    {"nome": "HALT NA MM 9 - TEND - PULLBACK", "descricao": "TRADE DE HALT NA MM 9 - A FAVOR DA TENDENCIA - PULLBACK"},
    {"nome": "PULBACK MAX/MIN DIA**", "descricao": "TRADE DE PULBACK NO PRÉ ROMP / PÓS ROMP / ROMP DE MAX/MIN DO DIA - ESPECIFICAR NO COMPLEMENTO"},
    {"nome": "POWER-BREAKOUT**", "descricao": "TRADE DE POWER-BREAKOUT - PÓS / PRÉ ROMPIMENTO - ESPECIFICAR NO COMPLEMENTO"},
    {"nome": "RANGE**", "descricao": "TRADE DE RANGE - ROMPIMENTO OU CONFIRMAÇÃO - ESPECIFICAR NO COMPLEMENTO"},
    {"nome": "REVERSÃO**", "descricao": "TRADE DE REVERSÃO APÓS MOVIMENTO DE VIOLENCIA (1-2-3 MARK CRISPY OU JOE DI NAPOLI) - ESPECIFICAR NO COMPLEMENTO"},
    {"nome": "VOLTA EM V**", "descricao": "TRADE DE VOLTA EM V - A FAVOR OU CONTRA TENDENCIA - - ESPECIFICAR NO COMPLEMENTO"},
    {"nome": "PIVOT ALINHADO MM-20 E MM-200", "descricao": "TRADE EM PIVOT ALINHADO COM A MM-20 E MM-200"},
    {"nome": "FIBO**", "descricao": "FIBO EPECIFICAR COMPLEMENTO"},
    {"nome": "SEM CONTEXTO", "descricao": "TRADE POR IMPULSO EMOCIONAL"},
    {"nome": "VWAP", "descricao": "TRADE VWAP"},
    {"nome": "TRICK ENTRY", "descricao": "TRICK ENTRY"},
    {"nome": "3º CANDLE 1 MINUTO", "descricao": "3º CANDLE 1 MINUTO"},
    {"nome": "ERRO", "descricao": "ERRO DIREÇÃO, BOTÃO, CONTA, ETC"},
    {"nome": "NOTÍCIA", "descricao": "EXECUTAR JUNTO A NOTICIA"},
    {"nome": "PIVÔ", "descricao": "PIVÔ"},
    {"nome": "PULBACK", "descricao": "PULBACK"},
    {"nome": "REENTRADA", "descricao": "REENTRADA "},
    {"nome": "PULBACK SUP/RES**", "descricao": "TRADE DE PULBACK NO PRÉ ROMP / PÓS ROMP / ROMP DE MAX/MIN DO DIA - ESPECIFICAR NO COMPLEMENTO"},
    {"nome": "5PI", "descricao": "REJEIÇÃO DE TOPO E FUNDO, SUP E RESIST"}
]

url = "http://127.0.0.1:8000/api/parametros?categoria=setups"

try:
    response = requests.post(url, json=setups_oficiais)
    if response.status_code == 200 or response.status_code == 201:
        print("Sucesso! Todos os 24 setups foram importados via API para o sistema.")
    else:
        print(f"Erro da API (Status {response.status_code}): {response.text}")
except Exception as e:
    print(f"Erro ao conectar com o servidor FastAPI: {e}")