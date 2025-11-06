"""
App Gestione Eventi - Sistema Integrato
Esplora eventi e chatta con AI - Due pagine in una
"""

import streamlit as st
import os

# Configurazione pagina principale
st.set_page_config(
    page_title="Gestione Eventi",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS comune per tutte le pagine
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .event-card {
        border-left: 4px solid #3498db;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    .insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .stat-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3498db;
    }
</style>
""", unsafe_allow_html=True)

# Inizializzazione session state globale
if "initialized" not in st.session_state:
    st.session_state.update({
        "api_key": None,
        "api_key_configured": False,
        "messages": [],
        "dataframe": None,
        "initialized": True
    })

# ==================== PAGINA HOME ====================
st.markdown('<div class="main-header">📊 Gestione Eventi</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <h3>👋 Benvenuto nel Sistema di Gestione Eventi!</h3>
    <p>Questo sistema ti permette di esplorare e analizzare i tuoi eventi in due modi:</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📊 Esplora Eventi
    
    **Visualizzazione classica con:**
    - 🗓️ Timeline cronologica
    - 🏷️ Analisi per categoria
    - 👥 Analisi per contatto
    - 🔍 Ricerca e filtri avanzati
    - ➕ Inserimento nuovi eventi
    - 📈 Insights e statistiche
    
    👉 **Vai alla pagina Esplora Eventi nel menu laterale**
    """)

with col2:
    st.markdown("""
    ### 🤖 Chat Eventi AI
    
    **Analisi intelligente con Claude:**
    - 💬 Domande in linguaggio naturale
    - 📊 Statistiche automatiche
    - 🔍 Ricerca semantica
    - 📈 Grafici su richiesta
    - 🤔 Insights e correlazioni
    - 💡 Suggerimenti intelligenti
    
    👉 **Vai alla pagina Chat Eventi AI nel menu laterale**
    """)

st.markdown("---")

# Verifica file Excel
EXCEL_FILE = "gestione_eventi.xlsx"
if os.path.exists(EXCEL_FILE):
    st.success(f"✅ File dati trovato: `{EXCEL_FILE}`")
    
    import pandas as pd
    try:
        df = pd.read_excel(EXCEL_FILE)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Totale Eventi", f"{len(df):,}")
        with col2:
            if 'CATEGORIA' in df.columns:
                st.metric("🏷️ Categorie", df['CATEGORIA'].nunique())
        with col3:
            if 'A CHI CHIEDERE' in df.columns:
                st.metric("👥 Contatti", df['A CHI CHIEDERE'].nunique())
        with col4:
            if 'DATA EVENTO' in df.columns:
                df['DATA EVENTO'] = pd.to_datetime(df['DATA EVENTO'], errors='coerce')
                future = len(df[df['DATA EVENTO'] >= pd.Timestamp.now()])
                st.metric("📅 Prossimi", future)
    except Exception as e:
        st.warning(f"⚠️ Errore lettura file: {str(e)}")
else:
    st.error(f"❌ File `{EXCEL_FILE}` non trovato nella directory corrente")
    st.info("💡 Assicurati che il file Excel sia nella stessa cartella dell'applicazione")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9rem;'>
    📊 Sistema Gestione Eventi - Versione Integrata<br>
    🔍 Esplorazione Visuale + 🤖 Analisi AI con Claude
</div>
""", unsafe_allow_html=True)
