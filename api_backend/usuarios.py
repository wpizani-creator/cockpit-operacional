"""
Módulo: frontend/views/usuarios.py
Descrição: Gerencia o cadastro e controle de usuários do cockpit com validação de senha forte.
"""

import streamlit as st
import re

def validar_senha_forte(senha: str) -> tuple[bool, str]:
    if len(senha) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres."
    if not re.search(r"[A-Z]", senha):
        return False, "A senha deve conter ao menos uma letra maiúscula."
    if not re.search(r"[a-z]", senha):
        return False, "A senha deve conter ao menos uma letra minúscula."
    if not re.search(r"\d", senha):
        return False, "A senha deve conter ao menos um número."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):
        return False, "A senha deve conter ao menos um caractere especial."
    return True, "Senha válida."

def renderizar():
    st.subheader("👤 Gerenciamento de Usuários")
    
    with st.form("form_usuario"):
        col1, col2 = st.columns(2)
        with col1:
            nome_usuario = st.text_input("Nome Completo")
            email = st.text_input("E-mail de Acesso")
        with col2:
            perfil = st.selectbox("Perfil de Acesso", ["Administrador", "Trader Operacional", "Analista"])
            senha = st.text_input("Senha de Acesso", type="password")
            
        salvar_usuario = st.form_submit_button("Cadastrar Novo Usuário")
        
        if salvar_usuario:
            if not nome_usuario or not email or not senha:
                st.warning("Preencha todos os campos obrigatórios.")
            else:
                valido, mensagem = validar_senha_forte(senha)
                if not valido:
                    st.error(mensagem)
                else:
                    st.success(f"Usuário {nome_usuario} cadastrado com sucesso com senha segura!")