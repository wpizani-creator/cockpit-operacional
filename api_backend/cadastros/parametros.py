"""
Módulo: frontend/views/cadastros/parametros.py
Descrição: Tela de cadastro e gerenciamento de parâmetros globais do sistema.
"""

import json
import os
import streamlit as st

# Caminho centralizado do arquivo de parâmetros
CAMINHO_CONFIG = os.path.join("database", "cadastros_config.json")


def _carregar_config():
    padrao = {
        "time_frames": ["1 min", "5 min", "15 min", "60 min", "Diário"],
        "tipos_entrada": ["Romp", "Reteste", "Abertura", "Ponto Contínuo"],
        "tipos_alvo": ["Alvo", "Fibo 100", "Fibo 161", "Parcial"],
        "tipos_saida": ["Alvo", "Stop", "Manual", "Inversão"],
        "setups": [
            "Setup Diamante",
            "Setup Supremo",
            "Rompimento 2º Candle",
            "WIN 15 min",
        ],
        "check_list": ["Ok", "Parcial", "Não"],
        "falha_principal": [
            "Nenhuma",
            "Atraso",
            "Ansiedade",
            "Fora do Setup",
            "Prematuro",
            "Excesso de Lotes",
        ],
    }

    os.makedirs(os.path.dirname(CAMINHO_CONFIG), exist_ok=True)

    if os.path.exists(CAMINHO_CONFIG):
        try:
            with open(CAMINHO_CONFIG, "r", encoding="utf-8") as f:
                dados = json.load(f)

            alterado = False
            for k, v in padrao.items():
                if k not in dados:
                    dados[k] = v
                    alterado = True

            if alterado:
                with open(CAMINHO_CONFIG, "w", encoding="utf-8") as f:
                    json.dump(dados, f, ensure_ascii=False, indent=4)
            return dados
        except Exception:
            pass

    with open(CAMINHO_CONFIG, "w", encoding="utf-8") as f:
        json.dump(padrao, f, ensure_ascii=False, indent=4)
    return padrao


def _salvar_config(dados):
    os.makedirs(os.path.dirname(CAMINHO_CONFIG), exist_ok=True)
    with open(CAMINHO_CONFIG, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def renderizar_parametros():
    st.markdown("## ⚙️ Cadastro de Parâmetros e Opções do Sistema")
    st.markdown(
        "Gerencie centralmente os valores e opções utilizados em todo o"
        " dashboard para evitar duplicações e erros de digitação."
    )
    st.markdown("---")

    config = _carregar_config()

    categorias = {
        "setups": "🚀 Nomes de Setup",
        "time_frames": "⏱️ Time Frames",
        "tipos_entrada": "📥 Tipos de Entrada",
        "tipos_alvo": "🎯 Tipos de Alvo",
        "tipos_saida": "📤 Tipos de Saída",
        "check_list": "📋 Check List",
        "falha_principal": "⚠️ Falha Principal",
    }

    cat_selecionada = st.selectbox(
        "Selecione a Categoria de Cadastro",
        options=list(categorias.keys()),
        format_func=lambda x: categorias[x],
    )

    st.markdown(f"### Gerenciar: {categorias[cat_selecionada]}")

    col1, col2 = st.columns([2, 1])

    lista_atual = config.get(cat_selecionada, [])

    with col1:
        st.markdown("**Opções Atuais Cadastradas:**")
        if lista_atual:
            for idx, item in enumerate(lista_atual):
                c_item1, c_item2 = st.columns([4, 1])
                with c_item1:
                    st.text(f"• {item}")
                with c_item2:
                    if st.button("🗑️ Excluir", key=f"del_{cat_selecionada}_{idx}"):
                        lista_atual.pop(idx)
                        config[cat_selecionada] = lista_atual
                        _salvar_config(config)
                        st.rerun()
        else:
            st.info("Nenhum item cadastrado nesta categoria.")

    with col2:
        st.markdown("**Adicionar Nova Opção:**")
        novo_valor = st.text_input(
            "Nome/Valor do Item", key=f"input_novo_{cat_selecionada}"
        )

        if st.button("➕ Salvar Novo Item", key=f"btn_add_{cat_selecionada}"):
            if novo_valor and novo_valor.strip():
                item_limpo = novo_valor.strip()
                if item_limpo not in lista_atual:
                    lista_atual.append(item_limpo)
                    config[cat_selecionada] = lista_atual
                    _salvar_config(config)
                    st.success(f"'{item_limpo}' adicionado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Este item já está cadastrado.")
            else:
                st.error("Digite um valor válido.")


render = renderizar_parametros

if __name__ == "__main__":
    renderizar_parametros()