"""
Módulo: frontend/views/cadastros/cadastro_contas.py
Descrição: Tela de cadastro e gerenciamento de contas, metas, IR, taxas e Dedo-Duro.
"""

import json
import os
import pandas as pd
import sqlite3
import streamlit as st

CAMINHO_CONFIG = os.path.join("database", "cadastros_config.json")
DB_PATH = os.path.join("database", "banco_trades.db")


def _carregar_configuracoes():
    if os.path.exists(CAMINHO_CONFIG):
        try:
            with open(CAMINHO_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"contas": []}


def _salvar_configuracoes(dados):
    os.makedirs(os.path.dirname(CAMINHO_CONFIG), exist_ok=True)
    with open(CAMINHO_CONFIG, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def _obter_contas_do_banco():
    contas_banco = []
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql(
                "SELECT DISTINCT conta_plataforma FROM trades_historico WHERE"
                " conta_plataforma IS NOT NULL AND conta_plataforma != ''",
                conn,
            )
            conn.close()
            if not df.empty:
                contas_banco = df["conta_plataforma"].astype(str).tolist()
        except Exception:
            pass
    return contas_banco


def render():
    st.subheader("⚙️ Cadastro de Contas, Metas e Taxas Operacionais")
    st.markdown(
        "Defina um apelido para sua conta, vincule-o ao número exato registrado"
        " na plataforma e configure taxas, metas e retenção de IR 'Dedo-Duro'."
    )

    dados = _carregar_configuracoes()
    if "contas" not in dados:
        dados["contas"] = []

    contas_detectadas = _obter_contas_do_banco()

    st.markdown("### ➕ Adicionar / Editar Configuração de Conta")

    with st.form("form_cadastro_conta", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome_conta = st.text_input(
                "Nome / Apelido da Conta (ex: Mesa Prop 5PI, Conta Principal)"
            )

            if contas_detectadas:
                numero_conta = st.selectbox(
                    "Número da Conta no Banco/Plataforma (Chave de Vínculo)",
                    contas_detectadas,
                )
            else:
                numero_conta = st.text_input(
                    "Número da Conta no Banco/Plataforma (ex: 103050571)"
                )

            meta_financeira = st.number_input(
                "Valor Meta Financeira (R$)", value=0.0, step=500.0
            )

        with col2:
            aliquota_ir = st.number_input(
                "Alíquota de IR sobre o Lucro (%)", value=20.0, step=1.0
            )
            taxa_win = st.number_input(
                "Taxa por Lote - Mini Índice (WIN) [R$]", value=1.0, step=0.1
            )
            taxa_wdo = st.number_input(
                "Taxa por Lote - Mini Dólar (WDO) [R$]", value=3.0, step=0.1
            )

        st.markdown("<br>", unsafe_allow_html=True)
        considerar_dedo_duro = st.checkbox(
            "Ativar retenção de IR 'Dedo-Duro' diário",
            value=True,
            help=(
                "Incide 1% no WIN e 0,005% no WDO sobre o saldo positivo diário"
                " do ativo."
            ),
        )

        submitted = st.form_submit_button(
            "💾 Salvar Configuração", type="primary"
        )

        if submitted:
            identificador_chave = numero_conta.strip() if numero_conta else ""
            if not identificador_chave:
                st.error(
                    "O número da conta é obrigatório para servir de ponte com o"
                    " histórico de trades."
                )
            else:
                contas = dados["contas"]
                encontrada = False
                for c in contas:
                    if (
                        str(c.get("numero")) == identificador_chave
                        or str(c.get("nome")) == identificador_chave
                    ):
                        c["nome"] = (
                            nome_conta.strip()
                            if nome_conta.strip()
                            else identificador_chave
                        )
                        c["numero"] = identificador_chave
                        c["meta"] = meta_financeira
                        c["ir_percentual"] = aliquota_ir
                        c["taxa_win"] = taxa_win
                        c["taxa_wdo"] = taxa_wdo
                        c["considerar_dedo_duro"] = considerar_dedo_duro
                        encontrada = True
                        break

                if not encontrada:
                    contas.append({
                        "nome": (
                            nome_conta.strip()
                            if nome_conta.strip()
                            else identificador_chave
                        ),
                        "numero": identificador_chave,
                        "meta": meta_financeira,
                        "ir_percentual": aliquota_ir,
                        "taxa_win": taxa_win,
                        "taxa_wdo": taxa_wdo,
                        "considerar_dedo_duro": considerar_dedo_duro,
                    })

                dados["contas"] = contas
                _salvar_configuracoes(dados)
                st.success(
                    "Configuração salva com sucesso para a conta ID:"
                    f" {identificador_chave}!"
                )
                st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Contas Configuradas Atualmente")

    if dados["contas"]:
        for i, c in enumerate(dados["contas"]):
            with st.container():
                cols = st.columns([2.5, 2, 2, 1.5, 1.5, 1])
                apelido_exibicao = c.get("nome", "")
                num_exibicao = c.get("numero", c.get("nome", ""))

                cols[0].markdown(
                    f"**Apelido:** {apelido_exibicao} <br><small"
                    f" style='color: gray;'>Conta: {num_exibicao}</small>",
                    unsafe_allow_html=True,
                )
                cols[1].markdown(f"Meta: R$ {c.get('meta', 0):,.2f}")
                cols[2].markdown(
                    f"Taxas (W/W): R$ {c.get('taxa_win', 0)} / R$"
                    f" {c.get('taxa_wdo', 0)}"
                )
                cols[3].markdown(f"IR: {c.get('ir_percentual', 0)}%")

                status_dd = (
                    "Sim ✅" if c.get("considerar_dedo_duro", True) else "Não ❌"
                )
                cols[4].markdown(f"Dedo-Duro: {status_dd}")

                if cols[5].button("🗑️ Excluir", key=f"del_conta_{i}"):
                    dados["contas"].pop(i)
                    _salvar_configuracoes(dados)
                    st.success("Configuração removida!")
                    st.rerun()
            st.markdown("---")
    else:
        st.info(
            "Nenhuma conta configurada ainda. Utilize o formulário acima para"
            " associar as regras."
        )


def renderizar_cadastro_contas():
    render()