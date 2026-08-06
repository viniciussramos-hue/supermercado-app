import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import io

st.set_page_config(page_title="🛒 Supermercado - IA Vision")

# --- CONFIGURAÇÃO DA IA ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ Chave da API do Google não encontrada! Configure-a no Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro-vision')

# --- FUNÇÃO DE IA PARA LER O PRODUTO ---
def analisar_foto_produto(imagem_pil):
    """Usa IA para extrair o nome do produto da foto."""
    prompt = """
    Analise a imagem fornecida, que é a embalagem de um produto de supermercado.
    Sua tarefa é identificar SOMENTE o NOME CLARO e a DESCRIÇÃO PRINCIPAL do produto (ex: "Polvilho Azedo 500g", "Leite Integral Italac 1L").
    Retorne apenas o texto do nome do produto, sem explicações ou aspas.
    Se não conseguir ler claramente, responda apenas com "Não consegui identificar".
    """
    try:
        response = model.generate_content([prompt, imagem_pil])
        return response.text.strip()
    except Exception as e:
        return f"Erro na IA: {e}"

# --- ESTADO DA APLICAÇÃO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Interface Principal
st.title("🛒 Supermercado - IA Vision")

st.subheader("1. Tire foto para o nome (IA)")
foto_input = st.camera_input("Apontar para embalagem do produto")

nome_ia = ""
if foto_input:
    try:
        img_bytes = foto_input.read()
        img_pil = Image.open(io.BytesIO(img_bytes))
        
        # Correção aplicada aqui (usando use_container_width)
        st.image(img_pil, caption="Foto capturada", use_container_width=True)
        
        with st.spinner("🧠 IA analisando a foto..."):
            nome_ia = analisar_foto_produto(img_pil)
            
            if nome_ia.startswith("Erro na IA") or nome_ia == "Não consegui identificar":
                st.error(f"A IA não conseguiu ler o nome: {nome_ia}")
                nome_ia = ""
            else:
                st.success(f"IA identificou: **{nome_ia}**")
                
    except Exception as e:
        st.error(f"Erro ao processar a imagem: {e}")

# Aba 2: Carrinho e Cadastro Manual
st.divider()
st.subheader("2. Detalhes do Item e Carrinho")

with st.form("form_item", clear_on_submit=True):
    col_a, col_b = st.columns(2)
    with col_a:
        nome_final = st.text_input("Nome do Produto:", value=nome_ia)
    with col_b:
        tipo_compra = st.radio("Tipo:", ["Unidade", "Quilo (Kg)"], horizontal=True)
        
    col1, col2 = st.columns(2)
    if tipo_compra == "Unidade":
        with col1:
            preco_unitario = st.number_input("Preço Unitário (R$):", min_value=0.0, format="%.2f", value=0.0)
        with col2:
            quantidade = st.number_input("Quantidade:", min_value=1, value=1, step=1)
        subtotal = preco_unitario * quantidade
        detalhe_texto = f"{quantidade} un"
    else:
        with col1:
            preco_kg = st.number_input("Preço por Kg (R$):", min_value=0.0, format="%.2f", value=0.0)
        with col2:
            peso = st.number_input("Peso (Kg):", min_value=0.001, format="%.3f", value=1.000, step=0.100)
        subtotal = preco_kg * peso
        detalhe_texto = f"{peso:.3f} kg"

    btn_adicionar = st.form_submit_button("Adicionar ao Carrinho", use_container_width=True)

if btn_adicionar:
    if nome_final and subtotal > 0:
        st.session_state.carrinho.append({
            "nome": nome_final,
            "detalhe": detalhe_texto,
            "subtotal": subtotal
        })
        st.success(f"Adicionado: {nome_final} ({detalhe_texto}) - R$ {subtotal:.2f}")
    else:
        st.error("Preencha o nome do produto e um preço/peso válido.")

# Exibindo o Carrinho
st.divider()
st.subheader("🛍️ Carrinho Atual")
total_geral = 0.0
if st.session_state.carrinho:
    for idx, item in enumerate(st.session_state.carrinho):
        st.write(f"**{idx+1}. {item['nome']}** ({item['detalhe']}) - **R$ {item['subtotal']:.2f}**")
        total_geral += item['subtotal']
    st.markdown(f"### Total Geral: R$ {total_geral:.2f}")
else:
    st.info("Carrinho vazio.")

if st.button("Limpar Tudo"):
    st.session_state.carrinho = []
    st.rerun()
