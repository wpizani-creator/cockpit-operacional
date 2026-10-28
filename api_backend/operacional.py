"""
Projeto: Cockpit Operacional API (Dashboard de Day Trade)
Módulo: frontend/views/operacional.py
Descrição: Roteador centralizado das telas operacionais e de cadastros.
Autor: Especialista / Analista Day Trade
Data: 2026-08-29
"""

import streamlit as st

# Importação dos módulos específicos de cadastro
try:
    from frontend.views.cadastros.cadastro_contas import render as render_cadastro_contas
except ImportError:
    try:
        from views.cadastros.cadastro_contas import render as render_cadastro_contas
    except ImportError:
        render_cadastro_contas = None

try:
    from frontend.views.cadastros.parametros import render as render_parametros_sistema
except ImportError:
    try:
        from views.cadastros.parametros import render as render_parametros_sistema
    except ImportError:
        render_parametros_sistema = None


def render_view(nav_opcao: str):
    # Removemos o caption duplicado daqui, pois o app.py já gerencia a exibição superior.
    
    if nav_opcao == "📊 Dados & Grade":
        st.title("📊 Dados & Grade Operacional")
        st.write("Visualização de preços, variação e livro de ofertas.")

    elif nav_opcao == "📈 Relatórios & Gráficos":
        st.title("📈 Relatórios & Gráficos de Performance")
        st.write("Análise gráfica dos resultados e evolução patrimonial.")

    elif nav_opcao == "📸 Análise Diária (IA)":
        st.title("📸 Análise Diária (IA)")
        st.write("Processamento e diagnósticos de inteligência artificial para a sessão de hoje.")

    elif nav_opcao == "📦 Análise em Lote (IA)":
        st.title("📦 Análise em Lote (IA)")
        st.write("Backtests consolidados e varredura de múltiplos arquivos.")

    elif nav_opcao == "📁 Histórico IA":
        st.title("📁 Histórico de Processamentos da IA")
        st.write("Logs anteriores e recomendações passadas armazenadas.")

    elif nav_opcao == "📝 Registro de Operações":
        st.title("📝 Registro de Operações")
        st.write("Lançamento manual ou automatizado de entradas e saídas.")

    elif nav_opcao == "📊 Gerenciar Operações":
        st.title("📊 Gerenciar Operações em Aberto")
        st.write("Acompanhamento de posições ativas, stops e alvos parciais.")

    elif nav_opcao == "📈 Análise Operações":
        st.title("📈 Análise Detalhada de Operações")
        st.write("Métricas de assertividade, payoff e fator de lucro.")

    elif nav_opcao == "📊 Visão Geral Consolidada":
        st.title("📊 Visão Geral Consolidada")
        st.write("Resumo geral da conta, resultados líquidos e metas atingidas.")

    elif nav_opcao == "⚙️ Cadastro de Parâmetros":
        if render_parametros_sistema:
            render_parametros_sistema()
        else:
            st.error("Erro: O arquivo 'parametros.py' não foi encontrado na pasta 'frontend/views/cadastros/'.")

    elif nav_opcao == "🏛️ Cadastro de Contas & Taxas":
        if render_cadastro_contas:
            render_cadastro_contas()
        else:
            st.error("Erro: O arquivo 'cadastro_contas.py' não foi encontrado na pasta 'frontend/views/cadastros/'.")

    elif nav_opcao == "📊 Importar Planilha (Google Sheets)":
        st.title("📊 Importação de Dados via Planilha")
        st.write("Sincronização de dados externos com o banco de dados.")

    elif nav_opcao == "⚙️ Configurar Indicadores":
        st.title("⚙️ Configuração de Indicadores Técnicos")
        st.write("Ajuste de médias móveis, VWAP, desvios e filtros de volatilidade.")

    elif nav_opcao == "💾 Backup & Restauração":
        st.title("💾 Backup & Restauração do Sistema")
        st.write("Exportação e segurança dos dados operacionais e logs.")
        
    else:
        st.title(f"Página: {nav_opcao}")
        st.write("Módulo em carregamento ou rota não mapeada.")