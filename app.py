import streamlit as st

# Título do App
st.title("🛒 Meu Supermercado - Lista de Compras")

# "Banco de dados" simulado de produtos (Código de Barras: Nome e Preço)
if 'produtos_db' not in st.session_state:
    st.session_state.produtos_db = {
        "7891000100103": {"nome": "Leite Integral 1L", "preco": 5.49},
        "7896004702116": {"nome": "Café Tradicional 500g", "preco": 18.90},
        "7891024115506": {"nome": "Arroz Branco 5kg", "preco": 24.50}
    }

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Campo para simular a leitura do código de barras (ou digitação)
codigo = st.text_input("Insira ou bipe o código de barras do produto:", key="input_codigo")

if codigo:
    if codigo in st.session_state.produtos_db:
        produto = st.session_state.produtos_db[codigo]
        st.session_state.carrinho.append(produto)
        st.success(f"Adicionado: {produto['nome']} - R$ {produto['preco']:.2f}")
    else:
        st.error("Produto não encontrado no sistema!")

# Exibindo o Carrinho e o Total
st.divider()
st.subheader("Itens no Carrinho")

total_geral = 0.0
if st.session_state.carrinho:
    for idx, item in enumerate(st.session_state.carrinho):
        st.write(f"{idx + 1}. {item['nome']} — **R$ {item['preco']:.2f}**")
        total_geral += item['preco']
    
    st.markdown(f"### Valor Total: R$ {total_geral:.2f}")
else:
    st.info("O carrinho está vazio.")

# Botão para limpar a lista
if st.button("Limpar Carrinho"):
    st.session_state.carrinho = []
    st.rerun()
