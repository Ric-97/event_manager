"""
Chat Eventi AI - Versione Semplice e Sicura con Claude
Analizza il file Excel eventi usando conversazioni naturali con Claude
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from anthropic import Anthropic

# Configurazione pagina
st.set_page_config(
    page_title="Chat Eventi AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
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

EXCEL_FILE = "gestione_eventi.xlsx"

# ==================== FUNZIONI UTILITY ====================

@st.cache_data(ttl=3600)
def load_excel_data():
    """Carica il file Excel degli eventi con caching"""
    if not os.path.exists(EXCEL_FILE):
        return None, "❌ File 'gestione_eventi.xlsx' non trovato"
    
    try:
        df = pd.read_excel(EXCEL_FILE)
        
        # Converti date
        if 'DATA EVENTO' in df.columns:
            df['DATA EVENTO'] = pd.to_datetime(df['DATA EVENTO'], errors='coerce', dayfirst=True)
        if 'TIMESTAMP INSERIMENTO' in df.columns:
            df['TIMESTAMP INSERIMENTO'] = pd.to_datetime(df['TIMESTAMP INSERIMENTO'], errors='coerce')
        if 'TIMESTAMP MODIFICA' in df.columns:
            df['TIMESTAMP MODIFICA'] = pd.to_datetime(df['TIMESTAMP MODIFICA'], errors='coerce')
        
        return df, None
    except Exception as e:
        return None, f"❌ Errore caricamento: {str(e)}"


def get_dataframe_summary(df):
    """Crea un sommario dettagliato del dataframe per Claude includendo TUTTI i dati"""
    
    # Informazioni base
    summary = f"""📊 **DATASET EVENTI - Informazioni Complete**

**Dimensioni:** {len(df):,} eventi × {len(df.columns)} colonne

**Colonne disponibili:**
{', '.join(df.columns.tolist())}

**Tipi di dati:**
"""
    for col, dtype in df.dtypes.items():
        summary += f"\n- {col}: {dtype}"
    
    # Statistiche per colonne categoriche
    summary += "\n\n**📈 Statistiche Categoriche:**"
    
    if 'CATEGORIA' in df.columns:
        cat_counts = df['CATEGORIA'].value_counts()
        summary += f"\n\n*Categorie ({len(cat_counts)} uniche):*"
        for cat, count in cat_counts.items():
            summary += f"\n  - {cat}: {count} eventi"
    
    if 'A CHI CHIEDERE' in df.columns:
        contact_counts = df['A CHI CHIEDERE'].value_counts()
        summary += f"\n\n*Contatti ({len(contact_counts)} unici):*"
        for contact, count in contact_counts.items():
            summary += f"\n  - {contact}: {count} eventi"
    
    # Statistiche temporali
    if 'DATA EVENTO' in df.columns:
        df_valid_dates = df[df['DATA EVENTO'].notna()]
        if len(df_valid_dates) > 0:
            min_date = df_valid_dates['DATA EVENTO'].min()
            max_date = df_valid_dates['DATA EVENTO'].max()
            summary += f"\n\n**📅 Range Temporale:**"
            summary += f"\n- Dal: {min_date.strftime('%d/%m/%Y')}"
            summary += f"\n- Al: {max_date.strftime('%d/%m/%Y')}"
            summary += f"\n- Durata: {(max_date - min_date).days} giorni"
            
            # Eventi passati vs futuri
            now = pd.Timestamp.now()
            past = len(df_valid_dates[df_valid_dates['DATA EVENTO'] < now])
            future = len(df_valid_dates[df_valid_dates['DATA EVENTO'] >= now])
            summary += f"\n- Eventi passati: {past}"
            summary += f"\n- Eventi futuri: {future}"
    
    # DATI COMPLETI in formato CSV
    summary += f"\n\n**📋 DATASET COMPLETO (tutti i {len(df)} eventi):**\n"
    summary += "\n```csv\n"
    
    # Converti il dataframe in CSV string
    # Formatta le date in modo leggibile
    df_copy = df.copy()
    for col in df_copy.columns:
        if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].dt.strftime('%d/%m/%Y %H:%M').fillna('')
    
    # Converti in CSV
    csv_string = df_copy.to_csv(index=False, sep=',', quoting=1)
    summary += csv_string
    summary += "```\n"
    
    summary += f"\n**💡 Nota:** Tutti i {len(df):,} eventi sono inclusi sopra in formato CSV. Analizza l'intero dataset per rispondere alle domande."
    
    return summary


def create_chart_from_intent(df, intent_type, x_col=None, y_col=None, color_col=None):
    """
    Crea grafici basati su intent predefiniti (SICURO - no code execution)
    """
    try:
        if intent_type == "categorie_distribuzione":
            if 'CATEGORIA' in df.columns:
                cat_counts = df['CATEGORIA'].value_counts()
                fig = px.pie(
                    values=cat_counts.values,
                    names=cat_counts.index,
                    title="Distribuzione Eventi per Categoria",
                    hole=0.4
                )
                return fig, "✅ Grafico creato"
            return None, "❌ Colonna CATEGORIA non trovata"
        
        elif intent_type == "contatti_top10":
            if 'A CHI CHIEDERE' in df.columns:
                top_contacts = df['A CHI CHIEDERE'].value_counts().head(10)
                fig = px.bar(
                    x=top_contacts.values,
                    y=top_contacts.index,
                    orientation='h',
                    title="Top 10 Contatti per Numero Eventi",
                    labels={'x': 'Numero Eventi', 'y': 'Contatto'},
                    color=top_contacts.values,
                    color_continuous_scale='Blues'
                )
                fig.update_layout(showlegend=False)
                return fig, "✅ Grafico creato"
            return None, "❌ Colonna A CHI CHIEDERE non trovata"
        
        elif intent_type == "timeline_eventi":
            if 'DATA EVENTO' in df.columns:
                df_time = df[df['DATA EVENTO'].notna()].copy()
                df_time['Mese'] = df_time['DATA EVENTO'].dt.to_period('M').astype(str)
                eventi_mese = df_time.groupby('Mese').size().reset_index(name='Numero Eventi')
                
                fig = px.line(
                    eventi_mese,
                    x='Mese',
                    y='Numero Eventi',
                    title='Trend Eventi nel Tempo',
                    markers=True
                )
                fig.update_traces(line_color='#3498db', line_width=3, marker_size=8)
                return fig, "✅ Grafico creato"
            return None, "❌ Colonna DATA EVENTO non trovata"
        
        elif intent_type == "heatmap_contatti_categorie":
            if 'A CHI CHIEDERE' in df.columns and 'CATEGORIA' in df.columns:
                pivot = pd.crosstab(df['A CHI CHIEDERE'], df['CATEGORIA'])
                top_contacts = df['A CHI CHIEDERE'].value_counts().head(10).index
                pivot_top = pivot.loc[top_contacts]
                
                fig = px.imshow(
                    pivot_top,
                    labels=dict(x="Categoria", y="Contatto", color="Eventi"),
                    x=pivot_top.columns,
                    y=pivot_top.index,
                    color_continuous_scale='Blues',
                    text_auto=True,
                    aspect='auto',
                    title="Matrice Contatti × Categorie (Top 10 Contatti)"
                )
                return fig, "✅ Grafico creato"
            return None, "❌ Colonne necessarie non trovate"
        
        elif intent_type == "custom_bar" and x_col and y_col:
            fig = px.bar(
                df,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f"{y_col} per {x_col}"
            )
            return fig, "✅ Grafico personalizzato creato"
        
        elif intent_type == "custom_scatter" and x_col and y_col:
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f"{y_col} vs {x_col}"
            )
            return fig, "✅ Grafico personalizzato creato"
        
        else:
            return None, "❌ Tipo di grafico non riconosciuto"
            
    except Exception as e:
        return None, f"❌ Errore creazione grafico: {str(e)}"


# ==================== INIZIALIZZAZIONE SESSION STATE ====================

if "initialized" not in st.session_state:
    st.session_state.update({
        "messages": [],
        "dataframe": None,
        "api_key": None,  # API key salvata nel session state
        "api_key_configured": False,
        "show_data_preview": False
    })
    st.session_state.initialized = True

# ==================== SIDEBAR: CONFIGURAZIONE ====================

with st.sidebar:
    st.markdown("### 🤖 Chat Eventi AI")
    st.markdown("*Powered by Claude 3.5 Sonnet*")
    st.markdown("---")
    
    # API Key Configuration
    st.subheader("🔑 Configurazione API")
    
    # Determina l'API key da usare
    api_key = None
    api_key_from_secrets = False
    
    # Priorità 1: Prova a caricare da Secrets file (per produzione)
    try:
        if hasattr(st, 'secrets') and "ANTHROPIC_API_KEY" in st.secrets and st.secrets["ANTHROPIC_API_KEY"]:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
            st.session_state.api_key = api_key
            st.session_state.api_key_configured = True
            api_key_from_secrets = True
    except Exception:
        # Secrets file non disponibile, passiamo alle altre opzioni
        pass
    
    # Mostra lo stato della configurazione
    if api_key_from_secrets:
        st.success("✅ API Key caricata da secrets file")
        st.caption("_Configurazione produzione attiva_")
    
    # Priorità 2: Session state (già inserita dall'utente)
    elif st.session_state.api_key:
        api_key = st.session_state.api_key
        st.session_state.api_key_configured = True
        st.success("✅ API Key configurata")
        
        # Mostra parte dell'API key (mascherata)
        masked_key = st.session_state.api_key[:15] + "..." + st.session_state.api_key[-4:]
        st.caption(f"_Key: `{masked_key}`_")
        
        # Pulsante per cancellare/modificare
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Modifica Key", use_container_width=True):
                st.session_state.api_key = None
                st.session_state.api_key_configured = False
                st.rerun()
        with col2:
            if st.button("🗑️ Rimuovi Key", use_container_width=True):
                st.session_state.api_key = None
                st.session_state.api_key_configured = False
                st.rerun()
    
    # Priorità 3: Input dall'utente
    else:
        st.info("👇 Inserisci la tua API Key Anthropic")
        
        api_key_input = st.text_input(
            "API Key",
            type="password",
            placeholder="sk-ant-api03-...",
            help="Inserisci la tua API key di Anthropic",
            key="api_key_input"
        )
        
        if api_key_input:
            # Validazione base del formato
            if api_key_input.startswith("sk-ant-"):
                if st.button("💾 Salva e Usa API Key", type="primary", use_container_width=True):
                    st.session_state.api_key = api_key_input
                    st.session_state.api_key_configured = True
                    api_key = api_key_input
                    st.success("✅ API Key salvata con successo!")
                    st.balloons()
                    st.info("🔄 Ricarico l'app...")
                    st.rerun()
            else:
                st.error("⚠️ Formato API Key non valido. Deve iniziare con 'sk-ant-'")
        
        # Istruzioni per ottenere l'API key
        with st.expander("❓ Come ottenere l'API Key"):
            st.markdown("""
            **Segui questi passaggi:**
            
            1. Vai su [console.anthropic.com](https://console.anthropic.com/)
            2. Crea un account o fai login
            3. Clicca su **"API Keys"** nel menu
            4. Clicca **"Create Key"**
            5. Copia la chiave (inizia con `sk-ant-api03-`)
            6. Incollala nel campo qui sopra
            7. Clicca **"Salva e Usa API Key"**
            
            ---
            
            **🔒 Sicurezza e Privacy:**
            
            ✅ La tua API key viene salvata **solo nella sessione corrente**  
            ✅ Non viene mai memorizzata permanentemente nel browser  
            ✅ Non viene mai inviata a server esterni (solo ad Anthropic)  
            ✅ Viene cancellata quando chiudi il browser  
            
            Per maggiore sicurezza in produzione, usa il file `.streamlit/secrets.toml` (vedi README.md).
            """)
        
        st.session_state.api_key_configured = False
    
    st.markdown("---")
    
    # Caricamento dati
    st.subheader("📊 Dati")
    
    if st.button("🔄 Ricarica Dati", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    df, error = load_excel_data()
    
    if error:
        st.error(error)
        st.session_state.dataframe = None
    else:
        st.session_state.dataframe = df
        st.success(f"✅ {len(df):,} eventi caricati")
        
        # Statistiche rapide
        st.metric("Totale Eventi", f"{len(df):,}")
        
        if 'CATEGORIA' in df.columns:
            st.metric("Categorie", df['CATEGORIA'].nunique())
        
        if 'A CHI CHIEDERE' in df.columns:
            st.metric("Contatti", df['A CHI CHIEDERE'].nunique())
        
        # Toggle preview
        if st.checkbox("👁️ Mostra Anteprima Dati"):
            st.dataframe(df.head(10), use_container_width=True)
    
    st.markdown("---")
    
    # Grafici rapidi (solo se dati caricati)
    if st.session_state.dataframe is not None:
        st.subheader("📈 Grafici Rapidi")
        
        chart_options = {
            "📊 Distribuzione Categorie": "categorie_distribuzione",
            "👥 Top 10 Contatti": "contatti_top10",
            "📅 Timeline Eventi": "timeline_eventi",
            "🔥 Heatmap Contatti×Categorie": "heatmap_contatti_categorie"
        }
        
        selected_chart = st.selectbox(
            "Seleziona grafico",
            options=list(chart_options.keys())
        )
        
        if st.button("📊 Genera Grafico", use_container_width=True):
            intent = chart_options[selected_chart]
            fig, msg = create_chart_from_intent(st.session_state.dataframe, intent)
            
            if fig:
                # Aggiungi a chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Ho generato il grafico richiesto: **{selected_chart}**",
                    "chart": fig
                })
                st.rerun()
            else:
                st.error(msg)
    
    st.markdown("---")
    
    # Esempi query (solo se API key configurata)
    st.subheader("💡 Esempi Query")
    
    if not st.session_state.api_key_configured:
        st.info("🔒 Configura l'API Key per usare gli esempi")
    else:
        esempi = [
            "Quanti eventi abbiamo in totale?",
            "Quali sono le categorie più popolari?",
            "Chi sono i contatti più attivi?",
            "Quali eventi sono previsti per i prossimi 30 giorni?",
            "Analizza il trend degli eventi nel tempo",
            "Quali sono le affinità tra i contatti?"
        ]
        
        for esempio in esempi:
            if st.button(f"💬 {esempio}", key=f"ex_{esempio[:20]}", use_container_width=True):
                # Simula l'invio della query
                st.session_state.temp_query = esempio
                st.rerun()
    
    st.markdown("---")
    
    if st.button("🗑️ Cancella Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ==================== MAIN INTERFACE ====================

st.markdown('<div class="main-header">🤖 Chat Eventi AI con Claude</div>', unsafe_allow_html=True)
st.caption("Esplora i tuoi eventi usando linguaggio naturale - Powered by Claude 3.5 Sonnet")

# Verifica prerequisiti
if not st.session_state.api_key_configured:
    st.warning("⚠️ **API Key non configurata**")
    st.info("""
    👈 **Configura la tua API Key Anthropic nella sidebar per iniziare:**
    
    1. Inserisci la tua API key nel campo nella sidebar
    2. Clicca su "Salva e Usa API Key"
    3. Inizia a chattare!
    
    💡 **Non hai un'API key?** Clicca su "Come ottenere l'API Key" nella sidebar per le istruzioni.
    """)
    st.stop()

if st.session_state.dataframe is None:
    st.warning("👈 **Carica i dati degli eventi per iniziare l'analisi**")
    st.stop()

# ==================== CHAT INTERFACE ====================

# Display chat history
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Mostra grafico se presente
        if "chart" in message and message["chart"] is not None:
            st.plotly_chart(message["chart"], use_container_width=True, key=f"chart_{i}")

# Gestione query da esempio
if "temp_query" in st.session_state:
    prompt = st.session_state.temp_query
    del st.session_state.temp_query
else:
    prompt = st.chat_input("Fai una domanda sugli eventi...", key="main_chat_input")

# Processa input
if prompt:
    df = st.session_state.dataframe
    
    # Aggiungi messaggio utente
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prepara context per Claude
    data_summary = get_dataframe_summary(df)
    
    # Avviso se il dataset è molto grande
    if len(df) > 1000:
        st.info(f"ℹ️ **Dataset di grandi dimensioni:** {len(df):,} eventi. L'analisi potrebbe richiedere qualche secondo in più...")
    
    # System prompt per Claude
    system_prompt = """Sei un assistente esperto nell'analisi di dati eventi per aziende.

Il tuo compito è aiutare l'utente a esplorare, analizzare e comprendere i dati degli eventi forniti.

**IMPORTANTE: Hai accesso al DATASET COMPLETO di tutti gli eventi in formato CSV.**
Non limitarti a un'anteprima - analizza tutti i dati forniti per dare risposte accurate e complete.

**Capacità:**
- Analisi statistica dettagliata dei dati completi
- Identificazione pattern e trend su tutto il dataset
- Risposta a domande specifiche analizzando tutti gli eventi
- Calcolo di statistiche precise (conteggi, medie, aggregazioni)
- Suggerimento di visualizzazioni appropriate
- Identificazione di affinità e relazioni tra contatti/categorie
- Analisi temporali e previsioni basate su tutti i dati storici

**Stile di risposta:**
- Sii conciso ma completo
- Usa emoji appropriate per rendere le risposte più leggibili
- Fornisci numeri e statistiche concrete basate su TUTTI i dati
- Se l'utente chiede conteggi o statistiche, analizza l'intero dataset CSV
- Se l'utente chiede un grafico, suggerisci quale tipo sarebbe più appropriato
- Rispondi SEMPRE in italiano

**Importante:**
- Basa le tue risposte SOLO sui dati forniti nel CSV completo
- Analizza TUTTI gli eventi, non solo un campione
- Se non hai informazioni sufficienti, dillo chiaramente
- Non inventare dati o statistiche
- Quando fai conteggi o aggregazioni, usa TUTTI i dati del CSV
"""
    
    # Costruisci il messaggio completo per Claude
    full_context = f"""{data_summary}

---

**Domanda dell'utente:** {prompt}

Analizza i dati forniti e rispondi alla domanda in modo chiaro e preciso."""
    
    # Genera risposta con Claude
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            with st.spinner("🤔 Sto analizzando i dati..."):
                # Usa l'API key dal session state
                if not st.session_state.api_key:
                    st.error("❌ API Key non configurata. Configura l'API key nella sidebar.")
                    st.stop()
                
                client = Anthropic(api_key=st.session_state.api_key)
                
                # Chiamata API Claude
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",  # Latest Claude Sonnet
                    max_tokens=4096,  # Aumentato per analisi complete
                    temperature=0,  # Deterministico per analisi dati
                    system=system_prompt,
                    messages=[{
                        "role": "user",
                        "content": full_context
                    }]
                )
                
                answer = response.content[0].text
                
                # Mostra risposta
                message_placeholder.markdown(answer)
                
                # Salva in history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })
                
        except Exception as e:
            error_msg = f"❌ **Errore durante l'elaborazione:**\n\n{str(e)}"
            
            # Gestisci errori comuni
            if "api_key" in str(e).lower():
                error_msg += "\n\n💡 Verifica che la tua API key sia corretta e attiva su console.anthropic.com"
            elif "rate limit" in str(e).lower():
                error_msg += "\n\n⏱️ Hai raggiunto il limite di richieste. Attendi qualche secondo e riprova."
            elif "overloaded" in str(e).lower():
                error_msg += "\n\n⚠️ Il servizio Claude è temporaneamente sovraccarico. Riprova tra poco."
            
            message_placeholder.error(error_msg)
            
            # Salva errore in history
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })

# ==================== INFO INIZIALE (se chat vuota) ====================

if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="info-box">
        <h3>👋 Benvenuto! Come posso aiutarti?</h3>
        <p>Sono qui per aiutarti ad esplorare e analizzare i tuoi eventi. Puoi chiedermi:</p>
        <ul>
            <li>📊 Statistiche generali (totali, medie, distribuzioni)</li>
            <li>🔍 Informazioni su eventi specifici</li>
            <li>👥 Analisi dei contatti e delle loro attività</li>
            <li>📅 Trend temporali e previsioni</li>
            <li>🤝 Affinità e relazioni tra categorie/contatti</li>
            <li>💡 Insight e opportunità nascoste nei dati</li>
        </ul>
        <p><strong>💡 Suggerimento:</strong> Usa gli esempi nella sidebar o scrivi la tua domanda nella chat!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostra statistiche chiave
    if st.session_state.dataframe is not None:
        df = st.session_state.dataframe
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="stat-card">
                <h4>📊 Totale Eventi</h4>
                <h2>{:,}</h2>
            </div>
            """.format(len(df)), unsafe_allow_html=True)
        
        with col2:
            if 'CATEGORIA' in df.columns:
                st.markdown("""
                <div class="stat-card">
                    <h4>🏷️ Categorie</h4>
                    <h2>{}</h2>
                </div>
                """.format(df['CATEGORIA'].nunique()), unsafe_allow_html=True)
        
        with col3:
            if 'A CHI CHIEDERE' in df.columns:
                st.markdown("""
                <div class="stat-card">
                    <h4>👥 Contatti</h4>
                    <h2>{}</h2>
                </div>
                """.format(df['A CHI CHIEDERE'].nunique()), unsafe_allow_html=True)
        
        with col4:
            if 'DATA EVENTO' in df.columns:
                df_future = df[df['DATA EVENTO'] >= pd.Timestamp.now()]
                st.markdown("""
                <div class="stat-card">
                    <h4>🔜 Prossimi Eventi</h4>
                    <h2>{}</h2>
                </div>
                """.format(len(df_future)), unsafe_allow_html=True)

# ==================== FOOTER ====================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8rem;'>
    🤖 Chat Eventi AI - Powered by Claude 3.5 Sonnet | 
    Analisi dati sicura e intelligente | 
    No code execution - 100% safe
</div>
""", unsafe_allow_html=True)