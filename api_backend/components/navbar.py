"""
Projeto: Cockpit Operacional API (Dashboard de Day Trade)
Módulo: frontend/components/navbar.py
Descrição: Barra de navegação horizontal com dropdown flutuante corrigido.
Autor: Especialista / Analista Day Trade
Data: 2026-08-29
"""

import streamlit.components.v1 as components


def render_navbar():
    menu_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {
            background-color: #0E1117;
            margin: 0;
            font-family: "Source Sans Pro", sans-serif;
            overflow: visible !important;
        }
        .top-navbar {
            display: flex;
            align-items: center;
            background-color: #0E1117;
            padding: 8px 16px;
            border-bottom: 1px solid #262730;
            gap: 30px;
            width: 100%;
            box-sizing: border-box;
            position: relative;
            z-index: 9999;
        }
        .nav-title {
            font-size: 16px;
            font-weight: 700;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            gap: 8px;
            white-space: nowrap;
        }
        .nav-menu-group {
            display: flex;
            gap: 12px;
            align-items: center;
        }
        .dropdown {
            position: relative;
            display: inline-block;
        }
        .dropbtn {
            background-color: transparent;
            color: #E5E7EB;
            padding: 8px 14px;
            font-size: 14px;
            font-weight: 500;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
        }
        .dropdown:hover .dropbtn {
            background-color: #1F2937;
            color: #38BDF8;
        }
        .dropdown-content {
            display: none;
            position: absolute;
            background-color: #1F2937;
            min-width: 260px;
            box-shadow: 0px 15px 35px rgba(0,0,0,0.8);
            border-radius: 8px;
            border: 1px solid #374151;
            z-index: 999999;
            top: 100%;
            left: 0;
            padding: 6px 0px;
            margin-top: 4px;
        }
        .dropdown-inner {
            background-color: #1F2937;
            border-radius: 8px;
        }
        .dropdown-content a {
            color: #E5E7EB;
            padding: 10px 18px;
            text-decoration: none;
            display: block;
            font-size: 13px;
            transition: background 0.15s, color 0.15s;
        }
        .dropdown-content a:hover {
            background-color: #374151;
            color: #38BDF8;
        }
        .dropdown:hover .dropdown-content {
            display: block;
        }
        .logout-btn {
            background-color: #7F1D1D;
            color: #FEE2E2;
            padding: 7px 14px;
            font-size: 13px;
            font-weight: 500;
            border: 1px solid #991B1B;
            border-radius: 6px;
            cursor: pointer;
            text-decoration: none;
            margin-left: auto;
            transition: background 0.2s;
            white-space: nowrap;
        }
        .logout-btn:hover {
            background-color: #991B1B;
            color: #FFFFFF;
        }
    </style>
    </head>
    <body>
        <div class="top-navbar">
            <div class="nav-title">📈 Cockpit Operacional</div>
            
            <div class="nav-menu-group">
                <div class="dropdown">
                    <button class="dropbtn">📁 Pré-Abertura & IA ▾</button>
                    <div class="dropdown-content">
                        <div class="dropdown-inner">
                            <a href="?nav=📊 Dados & Grade" target="_self">📊 Dados & Grade</a>
                            <a href="?nav=📈 Relatórios & Gráficos" target="_self">📈 Relatórios & Gráficos</a>
                            <a href="?nav=📸 Análise Diária (IA)" target="_self">📸 Análise Diária (IA)</a>
                            <a href="?nav=📦 Análise em Lote (IA)" target="_self">📦 Análise em Lote (IA)</a>
                            <a href="?nav=📁 Histórico IA" target="_self">📁 Histórico IA</a>
                        </div>
                    </div>
                </div>

                <div class="dropdown">
                    <button class="dropbtn">📁 Lançamento de Trades ▾</button>
                    <div class="dropdown-content">
                        <div class="dropdown-inner">
                            <a href="?nav=📝 Registro de Operações" target="_self">📝 Registro de Operações</a>
                            <a href="?nav=📊 Gerenciar Operações" target="_self">📊 Gerenciar Operações</a>
                            <a href="?nav=📈 Análise Operações" target="_self">📈 Análise Operações</a>
                        </div>
                    </div>
                </div>

                <div class="dropdown">
                    <button class="dropbtn">📁 Visão Geral & Histórico ▾</button>
                    <div class="dropdown-content">
                        <div class="dropdown-inner">
                            <a href="?nav=📊 Visão Geral Consolidada" target="_self">📊 Visão Geral Consolidada</a>
                        </div>
                    </div>
                </div>

                <div class="dropdown">
                    <button class="dropbtn">📁 Configurações & Cadastros ▾</button>
                    <div class="dropdown-content">
                        <div class="dropdown-inner">
                            <a href="?nav=⚙️ Cadastro de Parâmetros" target="_self">⚙️ Cadastro de Parâmetros</a>
                            <a href="?nav=🏛️ Cadastro de Contas & Taxas" target="_self">🏛️ Cadastro de Contas & Taxas</a>
                            <a href="?nav=📊 Importar Planilha (Google Sheets)" target="_self">📊 Importar Planilha (Google Sheets)</a>
                            <a href="?nav=⚙️ Configurar Indicadores" target="_self">⚙️ Configurar Indicadores</a>
                            <a href="?nav=💾 Backup & Restauração" target="_self">💾 Backup & Restauração</a>
                        </div>
                    </div>
                </div>
            </div>

            <a href="?fazer_logout=true" class="logout-btn" target="_self">🚪 Sair</a>
        </div>

        <script>
            document.querySelectorAll('.dropdown-content a, .logout-btn').forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    window.parent.location.href = this.href;
                });
            });
        </script>
    </body>
    </html>
    """
    # A altura foi aumentada para 300px no componente para dar espaço vertical aos submenus flutuantes
    components.html(menu_html, height=300)