import os
import streamlit as st
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="Dashboard Operacional - WIN/WDO",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Caminho absoluto ou relativo para a pasta de prints estruturada
PASTA_PRINTS = os.path.join("uploads", "prints")
os.makedirs(PASTA_PRINTS, exist_ok=True)

if "aba_ativa" not in st.session_state:
    st.session_state["aba_ativa"] = "📊 Dados & Grade"

# Simulação de base de dados em memória/sessão para testes do print
if "trades_exemplo" not in st.session_state:
    st.session_state["trades_exemplo"] = {
        101: {"ativo": "WINV26", "conta": "103050571", "print": None},
        102: {"ativo": "WDOV26", "conta": "103050571", "print": None}
    }

query_params = st.query_params
if "aba" in query_params:
    st.session_state["aba_ativa"] = query_params["aba"]

# Injeção do CSS avançado para efeito Hover (Passar o Mouse)
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { background-color: #0E1117; color: #FFFFFF; }

        /* Barra container principal dos menus */
        .custom-menubar {
            display: flex;
            gap: 12px;
            background-color: #161B22;
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid #30363D;
            margin-bottom: 20px;
            width: fit-content;
        }

        /* Cada item dropdown */
        .custom-dropdown {
            position: relative;
            display: inline-block;
        }

        /* Botão principal da pasta */
        .custom-dropbtn {
            background-color: #21262D;
            color: #C9D1D9;
            padding: 8px 14px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid #30363D;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            transition: background 0.15s ease;
        }

        .custom-dropbtn:hover {
            background-color: #30363D;
            color: #FFFFFF;
            border-color: #8B949E;
        }

        /* Caixa de conteúdo suspensa (Subpastas) */
        .custom-dropdown-content {
            display: none;
            position: absolute;
            background-color: #161B22;
            min-width: 220px;
            box-shadow: 0px 8px 24px rgba(0,0,0,0.6);
            border: 1px solid #30363D;
            border-radius: 6px;
            z-index: 99999;
            top: 100%;
            left: 0;
            margin-top: 4px;
            padding: 4px 0;
        }

        /* Links das subpastas */
        .custom-dropdown-content a {
            color: #C9D1D9;
            padding: 8px 14px;
            text-decoration: none;
            display: block;
            font-size: 13px;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            transition: background 0.1s;
        }

        .custom-dropdown-content a:hover {
            background-color: #1F6FEB;
            color: #FFFFFF;
        }

        /* Ativa a exibição ao passar o mouse */
        .custom-dropdown:hover .custom-dropdown-content {
            display: block;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Cabeçalho corporativo
st.markdown(
    """
    <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 8px; border-bottom: 1px solid #21262D; margin-bottom: 15px;">
        <h3 style="color: #FFFFFF; margin: 0; font-size: 18px;">📈 Cockpit Operacional (Streamlit)</h3>
        <span style="font-size: 11px; background: #1F6FEB; color: #FFF; padding: 2px 8px; border-radius: 10px;">Armazenamento Local Ativo</span>
    </div>
""",
    unsafe_allow_html=True,
)

# Menu HTML Puro com suporte a Hover nativo
menu_html = """
<div class="custom-menubar">
    <div class="custom-dropdown">
        <button class="custom-dropbtn">📁 Pré-Abertura & IA ▾</button>
        <div class="custom-dropdown-content">
            <a href="?aba=📊 Dados & Grade" target="_self">📊 Dados & Grade</a>
            <a href="?aba=📈 Relatórios & Gráficos" target="_self">📈 Relatórios & Gráficos</a>
            <a href="?aba=📸 Análise Diária (IA)" target="_self">📸 Análise Diária (IA)</a>
            <a href="?aba=📦 Análise em Lote (IA)" target="_self">📦 Análise em Lote (IA)</a>
            <a href="?aba=📁 Histórico IA" target="_self">📁 Histórico IA</a>
        </div>
    </div>

    <div class="custom-dropdown">
        <button class="custom-dropbtn">📁 Lançamento de Trades ▾</button>
        <div class="custom-dropdown-content">
            <a href="?aba=📝 Registro de Operações" target="_self">📝 Registro de Operações</a>
            <a href="?aba=📊 Gerenciar Operações" target="_self">📊 Gerenciar Operações</a>
            <a href="?aba=📈 Análise Operações" target="_self">📈 Análise Operações</a>
        </div>
    </div>

    <div class="custom-dropdown">
        <button class="custom-dropbtn">📁 Visão Geral & Histórico ▾</button>
        <div class="custom-dropdown-content">
            <a href="?aba=📊 Visão Geral Consolidada" target="_self">📊 Visão Geral Consolidada</a>
        </div>
    </div>

    <div class="custom-dropdown">
        <button class="custom-dropbtn">📁 Configurações & Cadastros ▾</button>
        <div class="custom-dropdown-content">
            <a href="?aba=⚙️ Cadastro de Parâmetros" target="_self">⚙️ Cadastro de Parâmetros</a>
            <a href="?aba=🏛️ Cadastro de Contas & Taxas" target="_self">🏛️ Cadastro de Contas & Taxas</a>
            <a href="?aba=📊 Importar Planilha (Google Sheets)" target="_self">📊 Importar Planilha</a>
            <a href="?aba=⚙️ Configurar Indicadores" target="_self">⚙️ Configurar Indicadores</a>
            <a href="?aba=💾 Backup & Restauração" target="_self">💾 Backup & Restauração</a>
        </div>
    </div>
</div>
"""

st.markdown(menu_html, unsafe_allow_html=True)

# Conteúdo Dinâmico da Aba Selecionada
aba_atual = st.session_state["aba_ativa"]

st.markdown(f"## {aba_atual}")
st.markdown(
    f"<p style='color: #8B949E; font-size: 13px; margin-bottom: 20px;'>Módulo operacional integrado em tempo real com alta performance.</p>",
    unsafe_allow_html=True,
)

with st.container():
    if aba_atual == "📊 Dados & Grade":
        st.markdown("### Gestão de Prints por Operação (Exemplo Prático)")
        st.info("Aqui os prints deixam de ser guardados no navegador e passam a ser salvos diretamente na pasta física do computador (`uploads/prints/`).")

        for trade_id, dados in st.session_state["trades_exemplo"].items():
            col1, col2, col3 = st.columns([2, 3, 3])
            with col1:
                st.write(f"**Trade ID:** {trade_id}")
                st.write(f"Ativo: {dados['ativo']}")
            with col2:
                # Componente nativo do Streamlit para upload do print da operação
                arquivo_upload = st.file_uploader(f"Carregar Print (ID {trade_id})", type=["png", "jpg", "jpeg"], key=f"up_{trade_id}")
                if arquivo_upload is not None:
                    # Salva fisicamente na pasta uploads/prints
                    nome_ficheiro = f"trade_{trade_id}_{dados['ativo']}.png"
                    caminho_completo = os.path.join(PASTA_PRINTS, nome_ficheiro)
                    
                    imagem = Image.open(arquivo_upload)
                    imagem.save(caminho_completo)
                    
                    # Guarda o caminho no dicionário de dados
                    st.session_state["trades_exemplo"][trade_id]["print"] = caminho_completo
                    st.success((f"Print guardado com sucesso em: {caminho_completo}"))
            
            with col3:
                if dados["print"] and os.path.exists(dados["print"]):
                    st.image(dados["print"], caption=f"Print do Trade {trade_id}", width=200)
                else:
                    st.warning("Nenhum print guardado para esta operação.")
            st.markdown("---")
    else:
        st.markdown(
            f"""
            <div style="background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 30px; text-align: center; color: #8B949E;">
                Ambiente carregado para a aba: <b style="color: #58A6FF;">{aba_atual}</b><br><br>
                Pronto para receber os componentes e tabelas de dados.
            </div>
        """,
            unsafe_allow_html=True,
        )