import streamlit as st

st.set_page_config(page_title="🛒 Supermercado Rápido", layout="centered")

# --- ESTADO DA APLICAÇÃO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

if 'favoritos' not in st.session_state:
    # Lista inicial de itens comuns para acesso rápido por toque
    st.session_state.favoritos = [
        "Leite Integral", "Café 500g", "Arroz 5kg", "Feijão 1kg", 
        "Açúcar", "Óleo de Soja", "Pão de Forma", "Ovos (Dúzia)", 
        "Papel Higiênico", "Frango (Kg)", "Carne Bovina (Kg)", "Tomate (Kg)"
    ]

# Título do Aplicativo
st.title("🛒 Supermercado Rápido")

# --- ABA 1: ADICIONAR ITENS ---
st.subheader("1. Adicionar ao Carrinho")

# Escolha do método de adição
modo_add = st.radio("Escolha como adicionar:", ["⚡ Botões Rápidos (Mais Usados)", "✍️ Digitar ou Ditar (Voz)"], horizontal=True)

nome_produto = ""

if modo_add.startswith("⚡"):
    st.write("Toque em um produto abaixo para selecionar:")
    # Cria botões em grade para toque rápido
    cols = st.columns(2)
    for idx, fav in enumerate(st.session_state.favoritos):
        with cols[idx % 2]:
            if st.button(f"➕ {fav}", use_container_width=True, key=f"fav_{idx}"):
                st.session_state.selecionado_temp = fav

    # Puxa o produto selecionado nos botões se houver
    nome_produto = st.session_state.get('selecionado_temp', '')
    if nome_produto:
        st.info(f"Produto selecionado: **{nome_produto}**")
else:
    # Campo manual ou por voz (o microfone do teclado do celular funciona aqui!)
    nome_produto = st.text_input("Nome do produto (ou use o microfone do teclado):", value="")

# Formulário para definir tipo, quantidade/peso e preço
if nome_produto:
    with st.form("form_detalhes", clear_on_submit=True):
        st.write(f"**Item:** {nome_produto}")
        
        tipo_compra = st.radio("Tipo de Medida:", ["Unidade", "Quilo (Kg)"], horizontal=True, key="tipo_medida")
        
        col1, col2 = st.columns(2)
        if tipo_compra == "Unidade":
            with col1:
                preco = st.number_input("Preço Unitário (R$):", min_value=0.0, format="%.2f", value=0.0)
            with col2:
                qtd = st.number_input("Quantidade:", min_value=1, value=1, step=1)
            subtotal = preco * qtd
            detalhe = f"{qtd} un"
        else:
            with col1:
                preco_kg = st.number_input("Preço por Kg (R$):", min_value=0.0, format="%.2f", value=0.0)
            with col2:
                peso = st.number_input("Peso (Kg):", min_value=0.001, format="%.3f", value=1.000, step=0.100)
            subtotal = preco_kg * peso
            detalhe = f"{peso:.3f} kg"

        btn_confirma = st.form_submit_button("✅ Confirmar e Adicionar", use_container_width=True)

        if btn_confirma:
            if subtotal > 0:
                st.session_state.carrinho.append({
                    "nome": nome_produto,
                    "detalhe": detalhe,
                    "subtotal": subtotal
                })
                # Limpa a seleção temporária
                if 'selecionado_temp' in st.session_state:
                    del st.session_state['selecionado_temp']
                st.success(f"Adicionado com sucesso!")
                st.rerun()
            else:
                st.error("Informe um preço válido maior que zero.")

st.divider()

# --- ABA 2: CARRINHO E TOTAL ---
st.subheader("🛍️ Seu Carrinho de Compras")

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
    st.info("Seu carrinho está vazio. Adicione itens acima!")
