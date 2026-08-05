import streamlit as st

st.title("🛒 Supermercado - Lista e Pesagem")

# Memória apenas com os nomes dos produtos que você já comprou
if 'produtos_memoria' not in st.session_state:
    st.session_state.produtos_memoria = [
        "Leite Integral 1L", 
        "Café Tradicional 500g", 
        "Arroz Branco 5kg", 
        "Paprica Picante",
        "Tomate",
        "Batata",
        "Carne Bovina"
    ]

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Escolha do modo de compra (Unidade ou Quilo)
tipo_compra = st.radio("Tipo de Item:", ["Unidade (Ex: caixas, pacotes)", "Peso / Quilo (Ex: carnes, verduras, legumes)"])

# Seção para adicionar item
st.subheader("Adicionar Item à Lista")

lista_nomes = sorted(st.session_state.produtos_memoria)
produto_selecionado = st.selectbox("Produto (ou digite um novo abaixo):", ["-- Selecionar da Lista --"] + lista_nomes)

# Permite digitar um nome caso não esteja na lista
nome_manual = st.text_input("Ou digite um nome novo se não estiver na lista:")

# Define qual nome usar
nome_final = nome_manual.strip() if nome_manual else (produto_selecionado if produto_selecionado != "-- Selecionar da Lista --" else "")

col1, col2 = st.columns(2)

if tipo_compra == "Unidade (Ex: caixas, pacotes)":
    with col1:
        preco_unitario = st.number_input("Preço Unitário (R$)", min_value=0.0, format="%.2f", value=0.0)
    with col2:
        quantidade = st.number_input("Quantidade (unidades)", min_value=1, value=1, step=1)
    
    subtotal = preco_unitario * quantidade
    detalhe_qtd = f"{quantidade} un"
else:
    with col1:
        preco_por_kg = st.number_input("Preço por Kg (R$)", min_value=0.0, format="%.2f", value=0.0)
    with col2:
        peso_kg = st.number_input("Peso (Kg) - ex: 0.750 ou 1.2", min_value=0.001, format="%.3f", value=1.000, step=0.100)
    
    subtotal = preco_por_kg * peso_kg
    detalhe_qtd = f"{peso_kg:.3f} kg"
    preco_unitario = preco_por_kg # para salvar no histórico

if st.button("Adicionar ao Carrinho", use_container_width=True):
    if nome_final and (preco_unitario > 0):
        # Adiciona à memória de nomes se for novo
        if nome_final not in st.session_state.produtos_memoria:
            st.session_state.produtos_memoria.append(nome_final)
        
        # Adiciona ao carrinho com os cálculos corretos
        st.session_state.carrinho.append({
            "nome": nome_final,
            "detalhe": detalhe_qtd,
            "subtotal": subtotal
        })
        st.success(f"Adicionado: {nome_final} ({detalhe_qtd}) — R$ {subtotal:.2f}")
        st.rerun()
    else:
        st.error("Informe o nome do produto e um preço válido.")

# Exibindo o Carrinho e o Total Geral
st.divider()
st.subheader("🛍️ Carrinho de Compras")

total_geral = 0.0
if st.session_state.carrinho:
    for idx, item in enumerate(st.session_state.carrinho):
        st.write(f"**{idx + 1}. {item['nome']}** ({item['detalhe']}) — **R$ {item['subtotal']:.2f}**")
        total_geral += item['subtotal']
    
    st.markdown(f"### Valor Total da Compra: R$ {total_geral:.2f}")
else:
    st.info("Nenhum item adicionado ainda.")

if st.button("Limpar Carrinho"):
    st.session_state.carrinho = []
    st.rerun()
