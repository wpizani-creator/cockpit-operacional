"""
Módulo: frontend/views/resumo.py
Descrição: Renderiza a tela de métricas e desempenho consolidado.
"""

import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

def renderizar():
    st.subheader("📊 Desempenho Consolidado")
    
    try:
        response = requests.get(f"{API_URL}/trades/resumo")
        if response.status_code == 200:
            dados = response.json()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total de Trades", dados.get("total_trades", 0))
            with col2:
                st.metric("Resultado Líquido", f"R$ {dados.get('resultado_liquido_total', 0.0):,.2f}")
            with col3:
                st.metric("Taxa de Acerto", f"{dados.get('taxa_acerto_pct', 0.0)}%")
            with col4:
                st.metric("Vencedores / Perdedores", f"{dados.get('trades_vencedores', 0)} / {dados.get('trades_perdedores', 0)}")
        else:
            st.error("Erro ao carregar o resumo da API.")
    except Exception as e:
        st.error(f"Não foi possível conectar à API FastAPI. Verifique se o servidor está rodando. Erro: {e}")