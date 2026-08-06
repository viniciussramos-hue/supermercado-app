import streamlit as st
import urllib.parse
import pandas as pd

st.set_page_config(page_title="🛒 Supermercado Rápido", layout="centered")

# --- ESTADO DA APLICAÇÃO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

if 'historico_frequentes' not in st.session_state:
    st.session_state.historico_frequentes = {
        "Leite Integral": 4.50,
        "Café 500g": 12.00,
        "Arroz 5kg": 22.90,
        "Feijão 1kg": 8.50,
        "Óleo de Soja": 7.00
    }

# Título do Aplicativo
st.title("🛒 Supermercado Rápido")

# --- ORÇAMENTO PRÉVIO ---
with st.sidebar:
    st.header("⚙️ Configurações")
    orcamento_max = st.number_input("Orçamento Máximo (R$):", min_value=0.0, format="%.2f", value=150.0)

st.subheader("Adicionar por Digitação ou Voz")
st.write("Digite ou fale (usando o microfone do teclado). Exemplos:")
st.write("• `batata 4.50 o kilo` (assume 1 kg)")
st.write("• `carne 2 kg 35.90` ou `2 leite 4.50`")

mapa_numeros = {
    "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "três": 3,
    "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10
}

def categorizar_produto(nome):
    nome_lower = nome.lower()
    if any(k in nome_lower for k in ["tomate", "cebola", "batata", "fruta", "banana", "maca", "alho", "cenoura", "alface"]):
        return "🍅 Hortifrúti"
    elif any(k in nome_lower for k in ["carne", "frango", "peixe", "linguiça", "bife"]):
        return "🥩 Açougue"
    elif any(k in nome_lower for k in ["sabao", "detergente", "papel", "limpeza", "esponja", "alvejante"]):
        return "🧹 Limpeza"
    else:
        return "📦 Mercearia / Outros"

# Formulário de entrada rápida
with st.form("form_adicionar", clear_on_submit=True):
    entrada_texto = st.text_input("O que vai levar?", placeholder="Ex: batata 4.50 o kilo ou carne 2 kg 35.90")
    btn_enviar = st.form_submit_button("➕ Adicionar ao Carrinho", use_container_width=True)

if btn_enviar and entrada_texto:
    texto_limpo = entrada_texto.lower()
    for termo in ["reais", "real", "r$", "o kilo", "o quilo", "quilo", "kilo", "kg", "litro", "l", "unidade", "un"]:
        texto_limpo = texto_limpo.replace(termo, "")
        
    partes = texto_limpo.strip().split()
    
    try:
        # Extrai todos os números presentes na frase limpa
        numeros_encontrados = []
        palavras_nome = []
        
        for p in partes:
            p_limpo = p.replace(',', '.')
            # Verifica se a parte é um número ou palavra de número
            if p_limpo.replace('.', '', 1).isdigit() or p in mapa_numeros:
                val = float(mapa_numeros[p]) if p in mapa_numeros else float(p_limpo)
                numeros_encontrados.append(val)
            else:
                palavras_nome.append(p)
                
        nome_bruto = " ".join(palavras_nome).strip()
        nome_detectado = " ".join([w.capitalize() for w in nome_bruto.split()])
        if not nome_detectado:
            nome_detectado = "Produto"
            
        # Lógica inteligente para identificar Preço e Quantidade dependendo de quantos números foram ditados
        if len(numeros_encontrados) >= 2:
            # Se tem dois números (ex: "batata 2 kg 4.50" ou "2 leite 4.50")
            # Assume que o menor ou o primeiro é a quantidade e o último é o preço unitário
            qtd_ou_peso = numeros_encontrados[0]
            preco_informado = numeros_encontrados[-1]
        elif len(numeros_encontrados) == 1:
            # Se digitou apenas o preço (ex: "batata 4.50 o kilo"), assume quantidade 1 por padrão
            qtd_ou_peso = 1.0
            preco_informado = numeros_encontrados[0]
        else:
            raise Exception("Nenhum valor numérico encontrado")
            
        subtotal = qtd_ou_peso * preco_informado
        categoria = categorizar_produto(nome_detectado)
        
        st.session_state.carrinho.append({
            "nome": nome_detectado,
            "qtd": qtd_ou_peso,
            "unitario": preco_informado,
            "subtotal": subtotal,
            "categoria": categoria
        })
        st.session_state.historico_frequentes[nome_detectado] = preco_informado
        
        st.success(f"Adicionado: {qtd_ou_peso}x {nome_detectado} - R$ {subtotal:.2f}")
        st.rerun()
            
    except Exception:
        st.warning("⚠️ Formato não reconhecido. Use o formato: `[Nome] [Preço]` (Ex: `batata 4.50`) ou `[Qtd] [Nome] [Preço]` (Ex: `2 leite 4.50`)")

# --- LISTA RECORRENTE / ITENS FREQUENTES ---
with st.expander("⚡ Adicionar Rápidos (Histórico Frequente)"):
    st.write("Clique em um item abaixo para adicioná-lo rapidamente (quantidade 1x):")
    cols_freq = st.columns(2)
    idx_col = 0
    for prod_freq, preco_freq in list(st.session_state.historico_frequentes.items())[:8]:
        with cols_freq[idx_col % 2]:
            if st.button(f"➕ {prod_freq} (R$ {preco_freq:.2f})", use_container_width=True):
                subtotal_freq = preco_freq
                cat_freq = categorizar_produto(prod_freq)
                st.session_state.carrinho.append({
                    "nome": prod_freq,
                    "qtd": 1.0,
                    "unitario": preco_freq,
                    "subtotal": subtotal_freq,
                    "categoria": cat_freq
                })
                st.rerun()
        idx_col += 1

st.divider()

# --- CARRINHO, TOTAL E ORÇAMENTO ---
st.subheader("🛍️ Seu Carrinho")

total_geral = 0.0
if st.session_state.carrinho:
    for item in st.session_state.carrinho:
        total_geral += item['subtotal']
        
    if orcamento_max > 0:
        progresso = min(total_geral / orcamento_max, 1.0)
        st.progress(progresso)
        if total_geral > orcamento_max:
            st.error(f"⚠️ Atenção! Você passou do orçamento máximo de R$ {orcamento_max:.2f}!")
        else:
            falta = orcamento_max - total_geral
            st.info(f"💡 Orçamento: R$ {total_geral:.2f} gastos de R$ {orcamento_max:.2f} (Restam R$ {falta:.2f})")

    st.markdown("---")

    for idx, item in enumerate(st.session_state.carrinho):
        col_item1, col_item2 = st.columns([4, 1])
        with col_item1:
            st.write(f"**{idx+1}. [{item['categoria']}] {item['nome']}** ({item['qtd']}x R$ {item['unitario']:.2f}) — **R$ {item['subtotal']:.2f}**")
        with col_item2:
            if st.button("❌", key=f"del_{idx}"):
                st.session_state.carrinho.pop(idx)
                st.rerun()
                
    st.markdown(f"--- \n### 💰 Total Geral: R$ {total_geral:.2f}")
    
    # --- BOTÃO DE EXPORTAR PARA EXCEL (CSV) ---
    df_export = pd.DataFrame(st.session_state.carrinho)
    df_export = df_export.rename(columns={
        "categoria": "Categoria",
        "nome": "Produto",
        "qtd": "Quantidade",
        "unitario": "Preço Unitário (R$)",
        "subtotal": "Subtotal (R$)"
    })
    csv_data = df_export.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📊 Baixar Planilha (Excel / CSV)",
        data=csv_data,
        file_name="lista_supermercado.csv",
        mime="text/csv",
        use_container_width=True
    )

    # --- BOTÃO DE EXPORTAR PARA O WHATSAPP ---
    texto_whatsapp = "🛒 *Minha Lista de Supermercado*\n\n"
    for item in st.session_state.carrinho:
        texto_whatsapp += f"• {item['nome']} ({item['qtd']}x R$ {item['unitario']:.2f}) - R$ {item['subtotal']:.2f}\n"
    texto_whatsapp += f"\n*Total Geral: R$ {total_geral:.2f}*"
    
    link_whatsapp = f"https://api.whatsapp.com/send?text={urllib.parse.quote(texto_whatsapp)}"
    
    st.markdown(
        f'<a href="{link_whatsapp}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; font-size:16px; cursor:pointer; margin-top: 5px;">📤 Enviar Lista para o WhatsApp</button></a>',
        unsafe_allow_html=True
    )
    
    st.write("") 
    if st.button("🗑️ Limpar Carrinho Inteiro", use_container_width=True):
        st.session_state.carrinho = []
        st.rerun()
else:
    st.info("Seu carrinho está vazio.")
