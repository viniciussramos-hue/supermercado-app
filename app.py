import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

st.set_page_config(page_title="🛒 Supermercado IA")

# --- CONFIGURAÇÃO DA IA ---
# Tenta pegar a chave do Streamlit Secrets (nuvem) ou de variável de ambiente (local)
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ Chave da API do Google não encontrada! Configure-a no Streamlit Secrets ou variáveis de ambiente.")
    st.stop()

genai.configure(api_key=api_key)

# Inicializa o modelo Gemini
model = genai.GenerativeModel('gemini-pro-vision')

# --- FUNÇÃO DE IA PARA LER O PRODUTO ---
def analisar_foto_produto(imagem_pil):
    """Usa IA para extrair o nome do produto da foto."""
    prompt = """
    Analise a imagem fornecida, que é a embalagem de um produto de supermercado.
    Sua tarefa é identificar SOMENTE o NOME CLARO e a DESCRIÇÃO PRINCIPAL do produto (ex: "Leite Integral Italac 1L", "Café Pilão 500g", "Sabonete Dove 90g").
    Não invente informações. Se não conseguir ler claramente, responda apenas com "Não consegui identificar".
    """
    try:
        response = model.generate_content([prompt, imagem_pil])
        return response.text.strip()
    except Exception as e:
        return f"Erro na IA: {e}"

# --- ESTADO DA APLICAÇÃO ---
if 'produtos_memoria' not in st.session_state:
    st.session_state.produtos_memoria = {} # Agora guarda nome -> preco

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Interface Principal
st.title("🛒 Supermercado - IA Vision")

# Aba 1: Adicionar com IA
st.subheader("1. Tire foto para o nome (IA)")
foto_input = st.camera_input("Apontar para embalagem do produto")

nome_ia = ""
if foto_input:
    # Mostra a foto tirada
    img = Image.open(foto_input)
    st.image(img, caption="Foto capturada", use_column_width=True)
    
    with st.spinner("🧠 IA analisando a foto..."):
        nome_ia = analisar_foto_produto(img)
        
        if nome_ia.startswith("Erro na IA") or nome_ia == "Não consegui identificar":
            st.error(f"A IA não conseguiu ler o nome: {nome_ia}")
        else:
            st.success(f"IA identificou: **{nome_ia}**")

# Aba 2: Carrinho e Cadastro Manual/Finalização
st.divider()
st.subheader("2. Detalhes do Item e Carrinho")

# Formulário para cadastrar o item (preenchido automaticamente pela IA ou manualmente)
with st.form("form_item"):
    col_a, col_b = st.columns(2)
    with col_a:
        # Preenche o campo nome com o que a IA achou (se tiver)
        nome_final = st.text_input("Nome do Produto:", value=nome_ia if foto_input else "", key="nome_final_input")
    with col_b:
        tipo_compra = st.radio("Tipo:", ["Unidade", "Quilo (Kg)"], horizontal=True)
        
    col1, col2 = st.columns(2)
    if tipo_compra == "Unidade":
        with col1:
            preco_unitario = st.number_input("Preço Unitário (R$):", min_value=0.0, format="%.2f", value=0.0, key="preco_uni_inp")
        with col2:
            quantidade = st.number_input("Quantidade:", min_value=1, value=1, step=1, key="qtd_inp")
        subtotal = preco_unitario * quantidade
        detalhe_texto = f"{quantidade} un"
    else:
        with col1:
            preco_kg = st.number_input("Preço por Kg (R$):", min_value=0.0, format="%.2f", value=0.0, key="preco_kg_inp")
        with col2:
            peso = st.number_input("Peso (Kg):", min_value=0.001, format="%.3f", value=1.000, step=0.100, key="peso_inp")
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
        # Opcional: limpa os campos do formulário para a próxima foto
        # st.rerun() 
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
