import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import io # Adicione esta importação no topo se não houver

# --- CONFIGURAÇÃO DA IA (Mantenha como estava) ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ Chave da API do Google não encontrada! Configure-a no Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro-vision')

# --- FUNÇÃO DE IA (CORRIGIDA E MELHORADA) ---
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

# --- ESTADO DA APLICAÇÃO (Mantenha como estava) ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Interface Principal
st.title("🛒 Supermercado - IA Vision")

st.subheader("1. Tire foto para o nome (IA)")
foto_input = st.camera_input("Apontar para embalagem do produto")

nome_ia = ""
# --- BLOCO PRINCIPAL CORRIGIDO ---
if foto_input:
    # CORREÇÃO DO ERRO: Lê o arquivo da câmera como imagem Pillow
    try:
        img_bytes = foto_input.read() # Lê os dados brutos da foto
        img_pil = Image.open(io.BytesIO(img_bytes)) # Converte para imagem Pillow
        
        # Exibe a imagem capturada corretamente
        st.image(img_pil, caption="Foto capturada", use_column_width=True)
        
        with st.spinner("🧠 IA analisando a foto..."):
            # Passa a imagem Pillow para a função
            nome_ia = analisar_foto_produto(img_pil)
            
            if nome_ia.startswith("Erro na IA") or nome_ia == "Não consegui identificar":
                st.error(f"A IA não conseguiu ler o nome: {nome_ia}")
            else:
                st.success(f"IA identificou: **{nome_ia}**")
                
    except Exception as e:
        st.error(f"Erro ao processar a imagem: {e}")

# Aba 2: Carrinho e Cadastro Manual
st.divider()
st.subheader("2. Detalhes do Item e Carrinho")

# Formulário (Mantenha como estava, mas garanta que o botão de submit usa a variável nome_ia)
with st.form("form_item"):
    col_a, col_b = st.columns(2)
    with col_a:
        # Preenche o campo nome com o que a IA achou (se tiver)
        nome_final = st.text_input("Nome do Produto:", value=nome_ia if foto_input and nome_ia else "", key="nome_final_input")
    with col_b:
        tipo_compra = st.radio("Tipo:", ["Unidade", "Quilo (Kg)"], horizontal=True)
    # ... (resto do formulário e carrinho) ...
