"""
Chatbot AI per Esplorazione Eventi Excel
Usa LangChain + Anthropic Claude per analisi dati interattiva con grafici
Versione compatibile - import robusti
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# LangChain imports - versione semplificata e robusta
from langchain_anthropic import ChatAnthropic

# Import agente - prova diverse varianti
try:
    from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
except ImportError:
    try:
        from langchain_experimental.agents import create_pandas_dataframe_agent
    except ImportError:
        from langchain.agents import create_pandas_dataframe_agent

# Configurazione pagina
st.set_page_config(
    page_title="Chat Eventi AI",
    page_icon="🤖",
    layout="wide"
)

# CSS personalizzato
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stTextInput input {
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

EXCEL_FILE = "gestione_eventi.xlsx"

# Funzione per caricare dati
@st.cache_data
def load_excel_data():
    """Carica il file Excel e prepara i dati"""
    if not os.path.exists(EXCEL_FILE):
        return None, "File Excel non trovato"
    
    try:
        df = pd.read_excel(EXCEL_FILE)
        
        # Converti date
        if 'DATA EVENTO' in df.columns:
            df['DATA EVENTO'] = pd.to_datetime(df['DATA EVENTO'], errors='coerce', dayfirst=True)
        
        # Prepara descrizione dataset
        info = f"""
Dataset Eventi:
- Totale eventi: {len(df)}
- Periodo: {df['DATA EVENTO'].min().strftime('%d/%m/%Y')} - {df['DATA EVENTO'].max().strftime('%d/%m/%Y')}
- Colonne: {', '.join(df.columns.tolist())}
- Categorie: {df['CATEGORIA'].nunique() if 'CATEGORIA' in df.columns else 'N/A'}
- Contatti: {df['A CHI CHIEDERE'].nunique() if 'A CHI CHIEDERE' in df.columns else 'N/A'}
"""
        return df, info
    except Exception as e:
        return None, f"Errore caricamento: {str(e)}"

# Funzione per creare grafici basati su richieste
def create_chart_from_query(df, query_result, query):
    """Crea grafici intelligenti basati sulla query e risultato"""
    
    query_lower = query.lower()
    
    # Determina tipo di grafico dalla query
    if any(word in query_lower for word in ['trend', 'tempo', 'evoluzione', 'mese', 'anno']):
        # Timeline
        if 'DATA EVENTO' in df.columns:
            df_time = df.copy()
            df_time['Mese'] = df_time['DATA EVENTO'].dt.to_period('M').astype(str)
            eventi_mese = df_time.groupby('Mese').size().reset_index(name='Numero Eventi')
            fig = px.line(eventi_mese, x='Mese', y='Numero Eventi', 
                         title='Trend Eventi nel Tempo', markers=True)
            return fig
    
    elif any(word in query_lower for word in ['categoria', 'tipo', 'distribuzione']):
        # Distribuzione categorie
        if 'CATEGORIA' in df.columns:
            cat_counts = df['CATEGORIA'].value_counts()
            fig = px.pie(values=cat_counts.values, names=cat_counts.index,
                        title='Distribuzione per Categoria', hole=0.4)
            return fig
    
    elif any(word in query_lower for word in ['contatto', 'persona', 'chi']):
        # Top contatti
        if 'A CHI CHIEDERE' in df.columns:
            top_contatti = df['A CHI CHIEDERE'].value_counts().head(10)
            fig = px.bar(x=top_contatti.values, y=top_contatti.index,
                        orientation='h', title='Top 10 Contatti',
                        labels={'x': 'Numero Eventi', 'y': 'Contatto'})
            return fig
    
    elif any(word in query_lower for word in ['confronta', 'compara', 'vs', 'matrice']):
        # Confronto categorie
        if 'CATEGORIA' in df.columns and 'A CHI CHIEDERE' in df.columns:
            pivot = pd.crosstab(df['CATEGORIA'], df['A CHI CHIEDERE'])
            top_contacts = df['A CHI CHIEDERE'].value_counts().head(5).index
            pivot_top = pivot[top_contacts]
            fig = px.imshow(pivot_top, 
                          labels=dict(x="Contatto", y="Categoria", color="Eventi"),
                          text_auto=True, aspect='auto',
                          title='Matrice Categorie x Contatti')
            return fig
    
    return None

# Inizializza session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "df" not in st.session_state:
    st.session_state.df = None

# Header
st.markdown('<div class="main-header">🤖 Chat Eventi AI</div>', unsafe_allow_html=True)
st.markdown("*Esplora i tuoi eventi con intelligenza artificiale*")

# Sidebar per configurazione
with st.sidebar:
    st.header("⚙️ Configurazione")
    
    # API Key Anthropic
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        help="Inserisci la tua chiave API di Anthropic"
    )
    
    if not api_key:
        st.warning("⚠️ Inserisci la tua API key per iniziare")
        st.info("""
        **Come ottenere la API key:**
        1. Vai su https://console.anthropic.com/
        2. Crea un account o fai login
        3. Vai su API Keys
        4. Crea una nuova chiave
        5. Copiala qui
        """)
    
    st.markdown("---")
    
    # Carica dati
    if st.button("🔄 Ricarica Dati Excel", use_container_width=True):
        st.cache_data.clear()
        st.session_state.df = None
        st.rerun()
    
    # Info dataset
    if st.session_state.df is None:
        df, info = load_excel_data()
        st.session_state.df = df
        st.session_state.dataset_info = info
    
    if st.session_state.df is not None:
        st.success("✅ Dati caricati")
        with st.expander("📊 Info Dataset"):
            st.text(st.session_state.dataset_info)
    else:
        st.error("❌ Dati non disponibili")
    
    st.markdown("---")
    
    # Esempi query
    st.subheader("💡 Esempi Query")
    esempi = [
        "Quanti eventi abbiamo in totale?",
        "Quali sono le categorie più popolari?",
        "Chi sono i top 5 contatti più attivi?",
        "Mostra il trend degli eventi nel tempo",
        "Quali eventi sono previsti per il prossimo mese?",
        "Trova affinità tra contatti",
        "Quali categorie stanno crescendo?"
    ]
    
    for esempio in esempi:
        if st.button(esempio, key=f"esempio_{esempio}", use_container_width=True):
            st.session_state.query_esempio = esempio
    
    st.markdown("---")
    
    if st.button("🗑️ Cancella Conversazione", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Funzione per processare query con LangChain
def process_query_with_langchain(query, df, api_key):
    """Processa la query usando LangChain + Anthropic"""
    
    try:
        # Inizializza Claude
        llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            anthropic_api_key=api_key,
            temperature=0,
            max_tokens=4096
        )
        
        # Crea agente pandas - usa parametri semplici compatibili
        agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=False,
            allow_dangerous_code=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
        
        # Prepara prompt contestuale
        contextualized_query = f"""
Sei un assistente esperto nell'analisi di dati eventi.

Dataset disponibile:
- Colonne: {', '.join(df.columns.tolist())}
- {len(df)} eventi totali
- Periodo: {df['DATA EVENTO'].min().strftime('%d/%m/%Y')} - {df['DATA EVENTO'].max().strftime('%d/%m/%Y')}

IMPORTANTE:
1. Basa la risposta SOLO sui dati del dataframe
2. Sii specifico e cita numeri esatti quando possibile
3. Se la domanda riguarda trend o confronti, menzionalo
4. Rispondi in italiano in modo chiaro e conciso
5. Se non hai dati sufficienti per rispondere, dillo chiaramente

Domanda dell'utente: {query}

Rispondi in modo diretto e professionale.
"""
        
        # Esegui query
        response = agent.invoke({"input": contextualized_query})
        
        # Estrai output
        if isinstance(response, dict):
            return response.get("output", str(response))
        else:
            return str(response)
        
    except Exception as e:
        error_msg = str(e)
        
        # Messaggi di errore più user-friendly
        if "API key" in error_msg.lower() or "authentication" in error_msg.lower():
            return "❌ Errore con l'API key. Verifica che sia corretta e attiva su console.anthropic.com"
        elif "rate limit" in error_msg.lower():
            return "⚠️ Limite rate raggiunto. Attendi qualche secondo e riprova."
        elif "timeout" in error_msg.lower():
            return "⏱️ Timeout. La query è troppo complessa. Prova a semplificarla."
        else:
            return f"❌ Errore durante l'elaborazione: {error_msg}\n\nProva a riformulare la domanda."

# Main chat interface
if api_key and st.session_state.df is not None:
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Mostra grafico se presente
            if "chart" in message and message["chart"] is not None:
                st.plotly_chart(message["chart"], use_container_width=True)
    
    # Chat input
    if "query_esempio" in st.session_state:
        prompt = st.session_state.query_esempio
        del st.session_state.query_esempio
    else:
        prompt = st.chat_input("Fai una domanda sugli eventi...")
    
    if prompt:
        # Aggiungi messaggio utente
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Genera risposta
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analizzo i dati..."):
                
                # Processa con LangChain
                response = process_query_with_langchain(
                    prompt, 
                    st.session_state.df, 
                    api_key
                )
                
                # Mostra risposta
                st.markdown(response)
                
                # Genera grafico se appropriato
                chart = create_chart_from_query(
                    st.session_state.df,
                    response,
                    prompt
                )
                
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "chart": chart
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })

elif not api_key:
    st.info("👈 Inserisci la tua **Anthropic API Key** nella sidebar per iniziare")
    
    st.markdown("""
    ### 🚀 Come Iniziare
    
    1. **Ottieni una API key Anthropic:**
       - Vai su https://console.anthropic.com/
       - Crea un account o fai login
       - Vai su API Keys
       - Genera una API key
    
    2. **Inserisci la chiave** nella sidebar
    
    3. **Inizia a chattare** con i tuoi dati!
    
    ### 💡 Cosa Puoi Chiedere
    
    - Statistiche e numeri
    - Trend temporali
    - Confronti tra categorie
    - Identificazione pattern
    - Affinità tra contatti
    - Potenzialità e opportunità
    
    ### 📊 Capacità
    
    - ✅ Analisi dati avanzata
    - ✅ Generazione grafici automatica
    - ✅ Risposte contestuali
    - ✅ Memoria conversazione
    - ✅ Suggerimenti intelligenti
    
    ### ⚙️ Setup Dipendenze
    
    Se hai errori di import, esegui:
    ```bash
    pip install --upgrade langchain langchain-anthropic langchain-experimental
    ```
    """)

else:
    st.error("❌ Impossibile caricare il file Excel. Verifica che 'gestione_eventi.xlsx' sia presente.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8rem;'>
    🤖 Chat Eventi AI - Powered by LangChain + Anthropic Claude<br>
    Analisi dati intelligente con visualizzazioni interattive
</div>
""", unsafe_allow_html=True)