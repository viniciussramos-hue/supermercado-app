import streamlit as st

st.title("🛒 Supermercado - Leitor de Código de Barras")

# Banco de dados simulado de produtos
if 'produtos_db' not in st.session_state:
    st.session_state.produtos_db = {
        "7891000100103": {"nome": "Leite Integral 1L", "preco": 5.49},
        "7896004702116": {"nome": "Café Tradicional 500g", "preco": 18.90},
        "7891024115506": {"nome": "Arroz Branco 5kg", "preco": 24.50}
    }

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Escolha do método de entrada para facilitar no celular
modo = st.radio("Escolha como adicionar o produto:", ["Digitar Código", "Usar Câmera do Celular"])

codigo = ""

if modo == "Digitar Código":
    codigo = st.text_input("Digite ou bipe o código de barras:")
else:
    st.info("Aponte a câmera traseira do celular para o código de barras:")
    # Ativa a câmera nativa do celular para tirar foto/capturar o frame
    foto_camera = st.camera_input("Tirar foto do código de barras")
    
    # Nota: Para leitura automática em tempo real via stream de vídeo, 
    # bibliotecas nativas de app (como Kivy) são exigidas. No Streamlit,
    # usamos a foto capturada ou um campo de texto rápido para o leitor bluetooth/manual.
    if foto_camera:
        st.warning("Capturado! Se estiver usando um leitor bluetooth portátil na porta USB/Bluetooth do celular, digite no campo manual.")

# Processamento do código inserido
if codigo:
    if codigo in st.session_state.produtos_db:
        produto = st.session_state.produtos_db[codigo]
        st.session_state.carrinho.append(produto)
        st.success(f"Adicionado: {produto['nome']} - R$ {produto['preco']:.2f}")
    else:
        st.error(f"Código '{codigo}' não cadastrado!")

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

if st.button("Limpar Carrinho"):
    st.session_state.carrinho = []
    st.rerun()
