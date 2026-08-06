import streamlit as st
import urllib.parse
import pandas as pd
import json
import os
import io
from datetime import datetime

st.set_page_config(page_title="🛒 Supermercado Rápido", layout="centered")

# --- ARQUIVO PARA SALVAR OS DADOS ---
ARQUIVO_DADOS = "dados_mercado.json"

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"orcamento_max": 150.0, "carrinho": []}

def salvar_dados():
    dados = {
        "orcamento_max": st.session_state.get("orcamento_max", 150.0),
        "carrinho": st.session_state.carrinho
    }
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

dados_salvos = carregar_dados()
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = dados_salvos["carrinho"]

st.title("🛒 Supermercado Rápido")

# --- ABA DE DASHBOARD E LISTA ---
tab1, tab2 = st.tabs(["🛍️ Lista Atual", "📊 Dashboard de Gastos"])

def categorizar_produto(nome):
    nome_lower = nome.lower()
    if any(k in nome_lower for k in ["tomate", "cebola", "batata", "fruta", "banana", "maca", "alho", "cenoura", "alface"]):
        return "🍅 Hortifrúti"
    elif any(k in nome_lower for k in ["carne", "frango", "peixe", "linguiça", "bife"]):
        return "🥩 Açougue"
    elif any(k in nome_lower for k in ["sabao", "detergente", "papel", "limpeza", "esponja", "alvejante"]):
        return "🧹 Limpeza"
    else:
        return "📦 Mercearia / Outros"

with tab1:
    with st.sidebar:
        st.header("⚙️ Configurações")
        orcamento_max = st.number_input("Orçamento Máximo (R$):", min_value=0.0, format="%.2f", 
                                        value=float(dados_salvos.get("orcamento_max", 150.0)), key="orcamento_max", on_change=salvar_dados)

    with st.form("form_adicionar", clear_on_submit=True):
        entrada_texto = st.text_input("O que vai levar?", placeholder="Ex: leite 4.50")
        btn_enviar = st.form_submit_button("➕ Adicionar ao Carrinho", use_container_width=True)

    if btn_enviar and entrada_texto:
        # Lógica simplificada de extração
        texto_limpo = entrada_texto.lower()
        # Removemos apenas termos que não são nomes de produtos
        termos_remover = ["reais", "real", "r$", "o kilo", "o quilo", "quilo", "kilo", "kg", "unidade", "un"]
        for termo in termos_remover:
            texto_limpo = texto_limpo.replace(termo, "")
        
        partes = texto_limpo.split()
        nome = " ".join([p.capitalize() for p in partes if not any(c.isdigit() for c in p)])
        precos = [float(p.replace(',', '.')) for p in partes if any(c.isdigit() for c in p)]
        
        if precos:
            preco = precos[-1]
            st.session_state.carrinho.append({
                "nome": nome if nome else "Produto",
                "qtd": 1.0,
                "unitario": preco,
                "subtotal": preco,
                "categoria": categorizar_produto(nome),
                "data": datetime.now().strftime("%Y-%m-%d")
            })
            salvar_dados()
            st.rerun()
        else:
            st.warning("Formato inválido. Ex: leite 4.50")

    # Lista
    total_geral = sum(item['subtotal'] for item in st.session_state.carrinho)
    for idx, item in enumerate(st.session_state.carrinho):
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{item['nome']}** — R$ {item['subtotal']:.2f}")
        if col2.button("❌", key=f"del_{idx}"):
            st.session_state.carrinho.pop(idx)
            salvar_dados()
            st.rerun()

with tab2:
    st.subheader("📈 Gastos por Categoria")
    if st.session_state.carrinho:
        df = pd.DataFrame(st.session_state.carrinho)
        gastos_cat = df.groupby('categoria')['subtotal'].sum()
        st.bar_chart(gastos_cat)
        st.write("### Detalhes")
        st.dataframe(df[['categoria', 'nome', 'subtotal', 'data']])
    else:
        st.info("Adicione itens para ver o dashboard.")
