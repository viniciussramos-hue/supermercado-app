import streamlit as st

st.set_page_config(page_title="🛒 Supermercado Rápido", layout="centered")

# --- ESTADO DA APLICAÇÃO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Título do Aplicativo
st.title("🛒 Supermercado Rápido")

st.subheader("Adicionar por Digitação ou Voz")
st.write("Digite ou fale (usando o microfone do teclado). Exemplos:")
st.write("• `3 leite 4.50` ou `dois arroz 22 reais` ou `1 café 12 e 50`")

mapa_numeros = {
    "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "três": 3,
    "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10
}

# Formulário com limpeza automática ao enviar
with st.form("form_adicionar", clear_on_submit=True):
    entrada_texto = st.text_input("O que vai levar?", placeholder="Ex: 2 arroz 22.90 ou dois leite 4 reais")
    btn_enviar = st.form_submit_button("➕ Adicionar ao Carrinho", use_container_width=True)

if btn_enviar and entrada_texto:
    # Remove palavras desnecessárias que a digitação por voz costuma trazer ("reais", "real", "e")
    texto_limpo = entrada_texto.lower()
    for termo in ["reais", "real", "r$"]:
        texto_limpo = texto_limpo.replace(termo, "")
    
    partes = texto_limpo.strip().split()
    
    try:
        # Converte quantidade (inicial)
        if partes and partes[0] in mapa_numeros:
            qtd_ou_peso = float(mapa_numeros[partes[0]])
            partes.pop(0)
        else:
            qtd_ou_peso = float(partes[0].replace(',', '.'))
            partes.pop(0)
            
        # Pega o preço (último elemento numérico da lista)
        # Se houver uma palavra "e" solta antes do centavo (ex: 4 e 50), trata ela
        if "e" in partes:
            partes.remove("e")
            
        preco_informado = float(partes[-1].replace(',', '.'))
        partes.pop(-1)
        
        # O restante no meio é o nome do produto
        nome_detectado = " ".join(partes).strip()
        if not nome_detectado:
            nome_detectado = "Produto"
            
        subtotal = qtd_ou_peso * preco_informado
        detalhe = f"{qtd_ou_peso} un/kg"
        
        st.session_state.carrinho.append({
            "nome": nome_detectado.capitalize(),
            "detalhe": detalhe,
            "subtotal": subtotal
        })
        st.success(f"Adicionado: {qtd_ou_peso}x {nome_detectado.capitalize()} - R$ {subtotal:.2f}")
        st.rerun()
            
    except Exception:
        st.warning("⚠️ Formato não reconhecido. Use o formato: `[Quantidade] [Nome] [Preço]` (Ex: `2 leite 4.50`)")

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
