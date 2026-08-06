import streamlit as st
import re

st.set_page_config(page_title="🛒 Supermercado Rápido", layout="centered")

# --- ESTADO DA APLICAÇÃO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Título do Aplicativo
st.title("🛒 Supermercado Rápido")

st.subheader("Adicionar por Digitação ou Voz")
st.write("Digite ou fale (usando o microfone do teclado) no formato: **[Quantidade] [Nome do Produto] [Preço]**")
st.write("*Exemplo:* `3 leite 4.50` ou `2 carne 35.90` ou `1 cafe 12.90`")

# Campo único de entrada rápida
entrada_texto = st.text_input("O que vai levar?", placeholder="Ex: 2 arroz 22.90")

if entrada_texto:
    # Tentativa de extração inteligente da frase
    # Procura números no texto para identificar quantidade e preço
    partes = entrada_texto.strip().split()
    
    # Validação simples para tentar extrair quantidade e preço
    try:
        # Assume que o primeiro número é a quantidade e o último é o preço
        # Ex: "3 leite 4.50" -> qtd = 3, preco = 4.50, nome = "leite"
        numeros = [p.replace(',', '.') for p in partes if p.replace(',', '').replace('.', '').isdigit()]
        
        if len(numeros) >= 2:
            qtd_ou_peso = float(numeros[0])
            preco_informado = float(numeros[-1])
            
            # O nome do produto é tudo o que está entre o primeiro e o último número
            inicio_nome = partes.index(numeros[0]) + 1
            fim_nome = len(partes) - 1 if partes[-1] == numeros[-1] else len(partes)
            nome_detectado = " ".join(partes[inicio_nome:fim_nome]).strip()
            if not nome_detectado:
                nome_detectado = "Produto"
            
            subtotal = qtd_ou_peso * preco_informado
            detalhe = f"{qtd_ou_peso} un/kg"
            
            # Botão de confirmação rápida com os dados interpretados
            st.info(êm := f"**Detectado:** {qtd_ou_peso}x {nome_detectado.capitalize()} a R$ {preco_informado:.2f} cada (Subtotal: R$ {subtotal:.2f})")
            
            if st.button("➕ Confirmar e Adicionar ao Carrinho", use_container_width=True):
                st.session_state.carrinho.append({
                    "nome": nome_detectado.capitalize(),
                    "detalhe": detalhe,
                    "subtotal": subtotal
                })
                st.success("Adicionado com sucesso!")
                st.rerun()
        else:
            st.warning("⚠️ Não consegui identificar a quantidade ou o preço. Use o formato: `[Quantidade] [Nome] [Preço]` (Ex: `2 leite 4.50`)")
    except Exception:
        st.warning("⚠️ Formato não reconhecido. Certifique-se de incluir a quantidade e o preço em números.")

st.divider()

# --- CARRINHO E TOTAL ---
st.subheader("🛍️ Seu Carrinho")

total_geral = 0.0
if st.session_state.carrinho:
    for idx, item in enumerate(st.session_state.carrinho):
        col_item1, col_item2 = st.columns([4, 1])
        with col_item1:
            st.write(f"**{idx+1}. {item['nome']}** ({item['detalhe']}) — **R$ {item['subtotal']:.2f}**")
        with col_item2:
            if st.button("❌", key=f"del_{idx}"):
                st.session_state.carrinho.pop(idx)
                st.rerun()
        total_geral += item['subtotal']
        
    st.markdown(f"--- \n### 💰 Total Geral: R$ {total_geral:.2f}")
    
    if st.button("🗑️ Limpar Carrinho Inteiro", use_container_width=True):
        st.session_state.carrinho = []
        st.rerun()
else:
    st.info("Seu carrinho está vazio.")
