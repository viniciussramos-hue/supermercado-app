import streamlit as st

st.set_page_config(page_title="🛒 Supermercado Rápido", layout="centered")

# --- ESTADO DA APLICAÇÃO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Título do Aplicativo
st.title("🛒 Supermercado Rápido")

st.subheader("Adicionar por Digitação ou Voz")
st.write("Digite ou fale (usando o microfone do teclado). Exemplos:")
st.write("• `3 leite 4.50` ou `dois arroz 22.90` ou `1 cafe 12.90`")

# Dicionário simples para converter números escritos em dígitos
mapa_numeros = {
    "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "três": 3,
    "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10
}

# Campo único de entrada rápida
entrada_texto = st.text_input("O que vai levar?", placeholder="Ex: 2 arroz 22.90 ou dois leite 4.50")

if entrada_texto:
    partes = entrada_texto.strip().lower().split()
    
    try:
        # Se a primeira palavra for um número escrito por extenso (ex: "dois"), converte para número
        if partes and partes[0] in mapa_numeros:
            qtd_ou_peso = float(mapa_numeros[partes[0]])
            # Remove a palavra do número da lista de partes para sobrar o nome e o preço
            partes.pop(0)
        else:
            # Tenta pegar o primeiro elemento como número normal
            qtd_ou_peso = float(partes[0].replace(',', '.'))
            partes.pop(0)
            
        # O último elemento da lista restante deve ser o preço unitário
        preco_informado = float(partes[-1].replace(',', '.'))
        partes.pop(-1) # Remove o preço
        
        # O que sobrou no meio é o nome do produto
        nome_detectado = " ".join(partes).strip()
        if not nome_detectado:
            nome_detectado = "Produto"
            
        subtotal = qtd_ou_peso * preco_informado
        detalhe = f"{qtd_ou_peso} un/kg"
        
        st.info(f"**Detectado:** {qtd_ou_peso}x {nome_detectado.capitalize()} a R$ {preco_informado:.2f} cada (Subtotal: R$ {subtotal:.2f})")
        
        if st.button("➕ Confirmar e Adicionar ao Carrinho", use_container_width=True):
            st.session_state.carrinho.append({
                "nome": nome_detectado.capitalize(),
                "detalhe": detalhe,
                "subtotal": subtotal
            })
            st.success("Adicionado com sucesso!")
            st.rerun()
            
    except Exception:
        st.warning("⚠️ Formato não reconhecido. Use o formato: `[Quantidade] [Nome] [Preço]` (Ex: `2 leite 4.50` ou `dois leite 4.50`)")

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
