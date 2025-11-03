import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Gestione Eventi", page_icon="📅", layout="wide")

# File Excel
EXCEL_FILE = "gestione_eventi.xlsx"

# Carica o crea il file
@st.cache_data
def load_data():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    else:
        return pd.DataFrame(columns=['DATA EVENTO', 'NOME EVENTO', 'LINK EVENTO', 
                                     'A CHI CHIEDERE', 'CATEGORIA', 
                                     'USER INSERIMENTO', 'TIMESTAMP INSERIMENTO',
                                     'USER MODIFICA', 'TIMESTAMP MODIFICA'])

def save_data(df):
    df.to_excel(EXCEL_FILE, index=False)
    st.cache_data.clear()

# Categorie disponibili
CATEGORIE = [
    'EVENTI sociali/politici/economici',
    'EVENTI delle organizzazioni',
    'EVENTI che interessano a logotel',
    'EVENTI di logotel che farà'
]

# Header
st.title("📅 Sistema Gestione Eventi")
st.markdown("---")

# Sidebar per login simulato
st.sidebar.header("👤 Utente")
username = st.sidebar.text_input("Username", value="admin", key="username")
st.sidebar.info(f"Connesso come: **{username}**")

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 Visualizza Eventi", "➕ Nuovo Evento", "✏️ Modifica Evento"])

# Carica dati
df = load_data()

# TAB 1: Visualizza Eventi
with tab1:
    st.header("Eventi Registrati")
    
    # Filtri
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_categoria = st.multiselect(
            "Filtra per Categoria",
            options=CATEGORIE,
            default=[]
        )
    
    with col2:
        filtro_persona = st.multiselect(
            "Filtra per Persona",
            options=df['A CHI CHIEDERE'].unique().tolist() if len(df) > 0 else [],
            default=[]
        )
    
    with col3:
        ordina_per = st.selectbox(
            "Ordina per",
            options=['DATA EVENTO', 'NOME EVENTO', 'TIMESTAMP INSERIMENTO'],
            index=0
        )
    
    # Applica filtri
    df_filtrato = df.copy()
    
    if filtro_categoria:
        df_filtrato = df_filtrato[df_filtrato['CATEGORIA'].isin(filtro_categoria)]
    
    if filtro_persona:
        df_filtrato = df_filtrato[df_filtrato['A CHI CHIEDERE'].isin(filtro_persona)]
    
    # Ordina
    if len(df_filtrato) > 0:
        df_filtrato = df_filtrato.sort_values(by=ordina_per)
    
    # Mostra statistiche
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Totale Eventi", len(df))
    with col2:
        st.metric("Eventi Filtrati", len(df_filtrato))
    with col3:
        if len(df) > 0:
            st.metric("Categorie", df['CATEGORIA'].nunique())
    with col4:
        if len(df) > 0:
            st.metric("Contatti", df['A CHI CHIEDERE'].nunique())
    
    st.markdown("---")
    
    # Mostra tabella
    if len(df_filtrato) > 0:
        # Converti date per visualizzazione
        df_display = df_filtrato.copy()
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
        
        # Download
        st.download_button(
            label="📥 Scarica Excel",
            data=open(EXCEL_FILE, 'rb').read(),
            file_name="eventi_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Nessun evento trovato con i filtri selezionati")

# TAB 2: Nuovo Evento
with tab2:
    st.header("Aggiungi Nuovo Evento")
    
    with st.form("nuovo_evento_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            data_evento = st.date_input("Data Evento*", datetime.now())
            nome_evento = st.text_input("Nome Evento*")
            categoria = st.selectbox("Categoria*", CATEGORIE)
        
        with col2:
            link_evento = st.text_input("Link Evento")
            persona = st.text_input("A Chi Chiedere*")
        
        submitted = st.form_submit_button("➕ Aggiungi Evento", use_container_width=True)
        
        if submitted:
            if nome_evento and persona:
                # Crea nuovo evento
                nuovo_evento = {
                    'DATA EVENTO': data_evento,
                    'NOME EVENTO': nome_evento,
                    'LINK EVENTO': link_evento,
                    'A CHI CHIEDERE': persona,
                    'CATEGORIA': categoria,
                    'USER INSERIMENTO': username,
                    'TIMESTAMP INSERIMENTO': datetime.now(),
                    'USER MODIFICA': '',
                    'TIMESTAMP MODIFICA': ''
                }
                
                # Aggiungi al dataframe
                df = pd.concat([df, pd.DataFrame([nuovo_evento])], ignore_index=True)
                save_data(df)
                
                st.success(f"✅ Evento '{nome_evento}' aggiunto con successo!")
                st.rerun()
            else:
                st.error("⚠️ Compila tutti i campi obbligatori (*)")

# TAB 3: Modifica Evento
with tab3:
    st.header("Modifica Evento Esistente")
    
    if len(df) > 0:
        # Seleziona evento
        eventi_lista = [f"{row['NOME EVENTO']} - {row['DATA EVENTO']}" 
                       for idx, row in df.iterrows()]
        
        evento_selezionato = st.selectbox(
            "Seleziona Evento da Modificare",
            options=range(len(eventi_lista)),
            format_func=lambda x: eventi_lista[x]
        )
        
        st.markdown("---")
        
        # Carica dati evento selezionato
        evento = df.iloc[evento_selezionato]
        
        with st.form("modifica_evento_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                data_evento_mod = st.date_input(
                    "Data Evento*",
                    value=pd.to_datetime(evento['DATA EVENTO'])
                )
                nome_evento_mod = st.text_input(
                    "Nome Evento*",
                    value=evento['NOME EVENTO']
                )
                categoria_mod = st.selectbox(
                    "Categoria*",
                    CATEGORIE,
                    index=CATEGORIE.index(evento['CATEGORIA'])
                )
            
            with col2:
                link_evento_mod = st.text_input(
                    "Link Evento",
                    value=evento['LINK EVENTO'] if pd.notna(evento['LINK EVENTO']) else ""
                )
                persona_mod = st.text_input(
                    "A Chi Chiedere*",
                    value=evento['A CHI CHIEDERE']
                )
            
            col_btn1, col_btn2 = st.columns([1, 1])
            
            with col_btn1:
                submitted_mod = st.form_submit_button(
                    "💾 Salva Modifiche",
                    use_container_width=True
                )
            
            with col_btn2:
                elimina = st.form_submit_button(
                    "🗑️ Elimina Evento",
                    use_container_width=True,
                    type="secondary"
                )
            
            if submitted_mod:
                if nome_evento_mod and persona_mod:
                    # Aggiorna evento
                    df.at[evento_selezionato, 'DATA EVENTO'] = data_evento_mod
                    df.at[evento_selezionato, 'NOME EVENTO'] = nome_evento_mod
                    df.at[evento_selezionato, 'LINK EVENTO'] = link_evento_mod
                    df.at[evento_selezionato, 'A CHI CHIEDERE'] = persona_mod
                    df.at[evento_selezionato, 'CATEGORIA'] = categoria_mod
                    df.at[evento_selezionato, 'USER MODIFICA'] = username
                    df.at[evento_selezionato, 'TIMESTAMP MODIFICA'] = datetime.now()
                    
                    save_data(df)
                    st.success("✅ Evento modificato con successo!")
                    st.rerun()
                else:
                    st.error("⚠️ Compila tutti i campi obbligatori (*)")
            
            if elimina:
                df = df.drop(evento_selezionato).reset_index(drop=True)
                save_data(df)
                st.success("✅ Evento eliminato con successo!")
                st.rerun()
        
        # Mostra metadati
        st.markdown("---")
        st.subheader("ℹ️ Metadati")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Inserito da:** {evento['USER INSERIMENTO']}")
            st.info(f"**Inserito il:** {evento['TIMESTAMP INSERIMENTO']}")
        with col2:
            if pd.notna(evento['USER MODIFICA']) and evento['USER MODIFICA']:
                st.info(f"**Modificato da:** {evento['USER MODIFICA']}")
                st.info(f"**Modificato il:** {evento['TIMESTAMP MODIFICA']}")
            else:
                st.info("**Nessuna modifica registrata**")
    else:
        st.info("Non ci sono eventi da modificare. Aggiungine uno nella tab 'Nuovo Evento'")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Sistema Gestione Eventi v1.0</div>",
    unsafe_allow_html=True
)
