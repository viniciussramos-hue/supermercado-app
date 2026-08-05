import streamlit as st

st.title("🛒 Supermercado - Leitura de Etiqueta e Totais")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

st.markdown("### Adicionar Item")

# Como a leitura direta de texto por IA pura exige servidores externos pesados, 
# facilitamos com um painel rápido otimizado para toque no celular:
nome_produto = st.text_input("Nome do Produto (ou tire foto da etiqueta para referência)")
foto_etiqueta = st.camera_input("Foto da etiqueta de preço")

col1, col2 = st.columns(2)
with col1:
    preco_unitario = st.number_input("Preço Unitário (R$)", min_value=0.0, format="%.2f", value=0.0)
with col2:
    quantidade = st.number_input("Quantidade", min_value=1, value=1, step=1)

if st.button("Adicionar à Lista", use_container_width=True):
    if nome_produto and preco_unitario > 0:
        subtotal = preco_unitario * quantidade
        st.session_state.carrinho.append({
            "nome": nome_produto,
            "preco_unit": preco_unitario,
            "qtd": quantidade,
            "subtotal": subtotal
        })
        st.success(p_msg := f"Adicionado: {quantidade}x {nome_produto} — R$ {subtotal:.2f}")
        st.rerun()
    else:
        st.error("Informe o nome e um preço unitário válido.")

# Exibindo o Carrinho e o Total Geral
st.divider()
st.subheader("🛍️ Carrinho de Compras")

total_geral = 0.0
if st.session_state.carrinho:
    for idx, item in enumerate(st.session_state.carrinho):
        st.write(f"**{idx + 1}. {item['nome']}**")
        st.write(f"   {item['qtd']}x R$ {item['preco_unit']:.2f} = **R$ {item['subtotal']:.2f}**")
        total_geral += item['subtotal']
    
    st.markdown(f"### Valor Total da Compra: R$ {total_geral:.2f}")
else:
    st.info("Nenhum item adicionado ainda.")

if st.button("Limpar Carrinho"):
    st.session_state.carrinho = []
    st.rerun()
