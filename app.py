import streamlit as st
import urllib.parse
import pandas as pd
import json
import os
import io
from datetime import datetime

st.set_page_config(page_title="🛒 Supermercado Rápido", layout="centered")

# --- ARQUIVO PARA SALVAR OS DADOS ---
ARQUIVO_DADOS = "dados_mercado.json"

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "orcamento_max": 150.0,
        "carrinho": [],
        "desejos": []
    }

def salvar_dados():
    dados = {
        "orcamento_max": st.session_state.get("orcamento_max", 150.0),
        "carrinho": st.session_state.carrinho,
        "desejos": st.session_state.desejos
    }
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# --- ESTADO DA APLICAÇÃO ---
dados_salvos = carregar_dados()

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = dados_salvos["carrinho"]

if 'desejos' not in st.session_state:
    st.session_state.desejos = dados_salvos.get("desejos", [])

# Título do Aplicativo
st.title("🛒 Supermercado Rápido")

# Abas do Aplicativo
tab1, tab2, tab3 = st.tabs(["🛍️ Lista Atual", "📊 Dashboard de Gastos", "⭐ Lista de Desejos"])

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

# --- ABA 1: LISTA ATUAL ---
with tab1:
    with st.sidebar:
        st.header("⚙️ Configurações")
        orcamento_max = st.number_input(
            "Orçamento Máximo (R$):", 
            min_value=0.0, 
            format="%.2f", 
            value=float(dados_salvos.get("orcamento_max", 150.0)),
            key="orcamento_max",
            on_change=salvar_dados
        )

    st.subheader("Adicionar por Digitação ou Voz")
    st.write("Ex: `leite 4.50` ou `2 carne 35.90`")

    with st.form("form_adicionar", clear_on_submit=True):
        entrada_texto = st.text_input("O que vai levar?", placeholder="Ex: leite 4.50")
        btn_enviar = st.form_submit_button("➕ Adicionar ao Carrinho", use_container_width=True)

    if btn_enviar and entrada_texto:
        texto_limpo = entrada_texto.lower()
        
        termos_remover = ["reais", "real", "r$", "o kilo", "o quilo", "quilo", "kilo", "kg", "unidade", "un"]
        for termo in termos_remover:
            texto_limpo = texto_limpo.replace(termo, "")
            
        palavras_texto = texto_limpo.split()
        palavras_filtradas = []
        for p in palavras_texto:
            if p == "l" or p == "litro" or p == "litros":
                continue
            palavras_filtradas.append(p)
            
        partes = palavras_filtradas
        
        try:
            numeros_encontrados = []
            palavras_nome = []
            
            for p in partes:
                p_limpo = p.replace(',', '.')
                if p_limpo.replace('.', '', 1).isdigit() or p in mapa_numeros:
                    val = float(mapa_numeros[p]) if p in mapa_numeros else float(p_limpo)
                    numeros_encontrados.append(val)
                else:
                    palavras_nome.append(p)
                    
            nome_bruto = " ".join(palavras_nome).strip()
            if not nome_bruto:
                nome_detectado = "Produto"
            else:
                nome_detectado = " ".join([w.capitalize() for w in nome_bruto.split()])
                
            if len(numeros_encontrados) >= 2:
                qtd_ou_peso = numeros_encontrados[0]
                preco_informado = numeros_encontrados[-1]
            elif len(numeros_encontrados) == 1:
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
                "categoria": categoria,
                "data": datetime.now().strftime("%Y-%m-%d")
            })
            
            salvar_dados()
            st.success(f"Adicionado: {qtd_ou_peso}x {nome_detectado} - R$ {subtotal:.2f}")
            st.rerun()
                
        except Exception:
            st.warning("⚠️ Formato não reconhecido. Use o formato: `[Nome] [Preço]` (Ex: `leite 4.50`)")

    st.divider()
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
                    salvar_dados()
                    st.rerun()
                    
        st.markdown(f"--- \n### 💰 Total Geral: R$ {total_geral:.2f}")
        
        # Botão Excel
        df_export = pd.DataFrame(st.session_state.carrinho)
        df_export = df_export.rename(columns={
            "categoria": "Categoria", "nome": "Produto", "qtd": "Quantidade",
            "unitario": "Preço Unitário (R$)", "subtotal": "Subtotal (R$)", "data": "Data"
        })
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name="Lista de Compras")
        excel_data = output.getvalue()

        st.download_button(
            label="📊 Baixar Planilha Excel (.xlsx)",
            data=excel_data,
            file_name="lista_supermercado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        # Botão WhatsApp
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
            salvar_dados()
            st.rerun()
    else:
        st.info("Seu carrinho está vazio.")

# --- ABA 2: DASHBOARD DE GASTOS ---
with tab2:
    st.subheader("📈 Gastos Acumulados por Categoria")
    if st.session_state.carrinho:
        df = pd.DataFrame(st.session_state.carrinho)
        gastos_cat = df.groupby('categoria')['subtotal'].sum()
        st.bar_chart(gastos_cat)
        st.write("### Histórico de Lançamentos")
        st.dataframe(df[['data', 'categoria', 'nome', 'qtd', 'unitario', 'subtotal']], use_container_width=True)
    else:
        st.info("Adicione itens ao carrinho para visualizar o dashboard.")

# --- ABA 3: LISTA DE DESEJOS ---
with tab3:
    st.subheader("⭐ Lista de Desejos (O que pretendo comprar)")
    
    with st.form("form_desejo", clear_on_submit=True):
        novo_desejo = st.text_input("Item que deseja comprar no futuro:", placeholder="Ex: Airfryer, Azeite importado...")
        btn_add_desejo = st.add_desejo_btn = st.form_submit_button("➕ Adicionar à Lista de Desejos", use_container_width=True)
        
    if btn_add_desejo and novo_desejo:
        st.session_state.desejos.append(novo_desejo.strip().capitalize())
        salvar_dados()
        st.success(f"Desejo adicionado: {novo_desejo}")
        st.rerun()
        
    st.markdown("---")
    if st.session_state.desejos:
        for idx, desejo in enumerate(st.session_state.desejos):
            col_d1, col_d2 = st.columns([4, 1])
            with col_d1:
                st.write(f"• {desejo}")
            with col_d2:
                if st.button("❌", key=f"del_desejo_{idx}"):
                    st.session_state.desejos.pop(idx)
                    salvar_dados()
                    st.rerun()
                    
        if st.button("🗑️ Limpar Lista de Desejos", use_container_width=True):
            st.session_state.desejos = []
            salvar_dados()
            st.rerun()
    else:
        st.info("Sua lista de desejos está vazia.")
