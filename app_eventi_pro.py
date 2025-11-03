import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from collections import Counter

st.set_page_config(
    page_title="Gestione Eventi Pro",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Custom
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #4472C4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .filter-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .event-card {
        border-left: 4px solid #4472C4;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    .priority-alta {
        border-left-color: #dc3545 !important;
    }
    .priority-media {
        border-left-color: #ffc107 !important;
    }
    .priority-bassa {
        border-left-color: #28a745 !important;
    }
</style>
""", unsafe_allow_html=True)

# File Excel
EXCEL_FILE = "gestione_eventi.xlsx"

# Categorie e opzioni
CATEGORIE = [
    'EVENTI sociali/politici/economici',
    'EVENTI delle organizzazioni',
    'EVENTI che interessano a logotel',
    'EVENTI di logotel che farà'
]

STATI = ['Pianificato', 'In Corso', 'Completato', 'Annullato']
PRIORITA = ['Alta', 'Media', 'Bassa']

# Funzioni di caricamento/salvataggio
@st.cache_data(ttl=1)
def load_data():
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        # Converti date
        if 'DATA EVENTO' in df.columns:
            df['DATA EVENTO'] = pd.to_datetime(df['DATA EVENTO'], errors='coerce')
        if 'TIMESTAMP INSERIMENTO' in df.columns:
            df['TIMESTAMP INSERIMENTO'] = pd.to_datetime(df['TIMESTAMP INSERIMENTO'], errors='coerce')
        if 'TIMESTAMP MODIFICA' in df.columns:
            df['TIMESTAMP MODIFICA'] = pd.to_datetime(df['TIMESTAMP MODIFICA'], errors='coerce')
        return df
    else:
        return pd.DataFrame()

def save_data(df):
    df.to_excel(EXCEL_FILE, index=False)
    st.cache_data.clear()

def get_color_by_priority(priority):
    colors = {'Alta': '#dc3545', 'Media': '#ffc107', 'Bassa': '#28a745'}
    return colors.get(priority, '#6c757d')

def get_color_by_status(status):
    colors = {
        'Pianificato': '#007bff',
        'In Corso': '#ffc107',
        'Completato': '#28a745',
        'Annullato': '#dc3545'
    }
    return colors.get(status, '#6c757d')

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/4472C4/FFFFFF?text=EVENTI+PRO", use_container_width=True)
    st.markdown("---")
    
    # User login
    st.subheader("👤 Utente")
    username = st.text_input("Username", value="admin", key="username")
    st.success(f"✓ Connesso come **{username}**")
    
    st.markdown("---")
    
    # Menu navigazione
    st.subheader("🧭 Navigazione")
    menu_option = st.radio(
        "Seleziona Vista",
        ["📊 Dashboard", "📅 Calendario", "⏱️ Timeline", "📋 Kanban Board", 
         "📑 Tabella Dati", "➕ Nuovo Evento", "✏️ Modifica Evento", 
         "📈 Analytics"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick stats
    df = load_data()
    if len(df) > 0:
        st.subheader("⚡ Quick Stats")
        st.metric("Totale Eventi", len(df))
        st.metric("In Corso", len(df[df['STATO'] == 'In Corso']))
        st.metric("Completati", len(df[df['STATO'] == 'Completato']))
    
    st.markdown("---")
    st.caption("v2.0 Pro Edition")

# Main content
st.markdown('<div class="main-header">📅 Sistema Gestione Eventi Pro</div>', unsafe_allow_html=True)

# Carica dati
df = load_data()

# ========== DASHBOARD ==========
if menu_option == "📊 Dashboard":
    st.header("Dashboard Overview")
    
    if len(df) > 0:
        # KPI Cards
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("📌 Totale Eventi", len(df))
        with col2:
            eventi_futuro = len(df[df['DATA EVENTO'] >= datetime.now()])
            st.metric("🔜 Prossimi Eventi", eventi_futuro)
        with col3:
            eventi_mese = len(df[
                (df['DATA EVENTO'].dt.month == datetime.now().month) &
                (df['DATA EVENTO'].dt.year == datetime.now().year)
            ])
            st.metric("📅 Questo Mese", eventi_mese)
        with col4:
            alta_priorita = len(df[df['PRIORITÀ'] == 'Alta'])
            st.metric("🔥 Alta Priorità", alta_priorita)
        with col5:
            completati = len(df[df['STATO'] == 'Completato'])
            perc = (completati / len(df) * 100) if len(df) > 0 else 0
            st.metric("✅ Completamento", f"{perc:.0f}%")
        
        st.markdown("---")
        
        # Grafici
        col1, col2 = st.columns(2)
        
        with col1:
            # Eventi per categoria
            st.subheader("📊 Eventi per Categoria")
            cat_counts = df['CATEGORIA'].value_counts()
            fig_cat = px.pie(
                values=cat_counts.values,
                names=cat_counts.index,
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_cat.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_cat, use_container_width=True)
        
        with col2:
            # Stati eventi
            st.subheader("📈 Distribuzione Stati")
            stato_counts = df['STATO'].value_counts()
            colors_stato = [get_color_by_status(s) for s in stato_counts.index]
            fig_stato = go.Figure(data=[go.Bar(
                x=stato_counts.index,
                y=stato_counts.values,
                marker_color=colors_stato,
                text=stato_counts.values,
                textposition='auto'
            )])
            fig_stato.update_layout(
                xaxis_title="Stato",
                yaxis_title="Numero Eventi",
                showlegend=False
            )
            st.plotly_chart(fig_stato, use_container_width=True)
        
        # Timeline mensile
        st.subheader("📆 Eventi per Mese")
        df_timeline = df.copy()
        df_timeline['Mese'] = df_timeline['DATA EVENTO'].dt.to_period('M').astype(str)
        eventi_mese = df_timeline.groupby('Mese').size().reset_index(name='Numero Eventi')
        
        fig_timeline = px.line(
            eventi_mese,
            x='Mese',
            y='Numero Eventi',
            markers=True,
            line_shape='spline'
        )
        fig_timeline.update_traces(line_color='#4472C4', line_width=3)
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Priorità vs Categoria
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Priorità")
            prior_counts = df['PRIORITÀ'].value_counts()
            colors_prior = [get_color_by_priority(p) for p in prior_counts.index]
            fig_prior = go.Figure(data=[go.Bar(
                x=prior_counts.index,
                y=prior_counts.values,
                marker_color=colors_prior,
                text=prior_counts.values,
                textposition='auto'
            )])
            fig_prior.update_layout(showlegend=False)
            st.plotly_chart(fig_prior, use_container_width=True)
        
        with col2:
            st.subheader("👥 Top Contatti")
            top_persone = df['A CHI CHIEDERE'].value_counts().head(10)
            fig_persone = px.bar(
                x=top_persone.values,
                y=top_persone.index,
                orientation='h',
                color=top_persone.values,
                color_continuous_scale='Blues'
            )
            fig_persone.update_layout(showlegend=False, yaxis_title="", xaxis_title="Numero Eventi")
            st.plotly_chart(fig_persone, use_container_width=True)
    else:
        st.info("📭 Nessun evento nel database. Aggiungine uno per iniziare!")

# ========== CALENDARIO ==========
elif menu_option == "📅 Calendario":
    st.header("Vista Calendario")
    
    if len(df) > 0:
        # Selezione mese
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            mese_selezionato = st.date_input(
                "Seleziona Mese",
                value=datetime.now(),
                key="cal_month"
            )
        
        # Filtra eventi per mese
        mese = mese_selezionato.month
        anno = mese_selezionato.year
        
        df_mese = df[
            (df['DATA EVENTO'].dt.month == mese) &
            (df['DATA EVENTO'].dt.year == anno)
        ].copy()
        
        st.markdown(f"### 📅 {mese_selezionato.strftime('%B %Y')}")
        st.markdown(f"**{len(df_mese)} eventi in questo mese**")
        
        if len(df_mese) > 0:
            # Raggruppa per giorno
            df_mese['Giorno'] = df_mese['DATA EVENTO'].dt.day
            
            # Mostra eventi giorno per giorno
            for giorno in sorted(df_mese['Giorno'].unique()):
                eventi_giorno = df_mese[df_mese['Giorno'] == giorno]
                data_str = f"{giorno:02d}/{mese:02d}/{anno}"
                
                with st.expander(f"📅 {data_str} - {len(eventi_giorno)} eventi", expanded=True):
                    for _, evento in eventi_giorno.iterrows():
                        priority_class = f"priority-{evento['PRIORITÀ'].lower()}" if pd.notna(evento['PRIORITÀ']) else ""
                        st.markdown(f"""
                        <div class="event-card {priority_class}">
                            <strong>{evento['NOME EVENTO']}</strong><br>
                            <small>
                                🏷️ {evento['CATEGORIA']}<br>
                                👤 {evento['A CHI CHIEDERE']}<br>
                                📊 Stato: <strong>{evento['STATO']}</strong> | 
                                🎯 Priorità: <strong>{evento['PRIORITÀ']}</strong>
                            </small>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("📭 Nessun evento in questo mese")
    else:
        st.info("📭 Nessun evento nel database")

# ========== TIMELINE ==========
elif menu_option == "⏱️ Timeline":
    st.header("Timeline Cronologica")
    
    if len(df) > 0:
        # Filtri
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_cat = st.multiselect("Categoria", CATEGORIE, default=[])
        with col2:
            filtro_stato = st.multiselect("Stato", STATI, default=[])
        with col3:
            filtro_prior = st.multiselect("Priorità", PRIORITA, default=[])
        
        # Applica filtri
        df_filtered = df.copy()
        if filtro_cat:
            df_filtered = df_filtered[df_filtered['CATEGORIA'].isin(filtro_cat)]
        if filtro_stato:
            df_filtered = df_filtered[df_filtered['STATO'].isin(filtro_stato)]
        if filtro_prior:
            df_filtered = df_filtered[df_filtered['PRIORITÀ'].isin(filtro_prior)]
        
        df_filtered = df_filtered.sort_values('DATA EVENTO')
        
        st.markdown(f"**Visualizzazione {len(df_filtered)} eventi**")
        
        # Timeline Gantt
        if len(df_filtered) > 0:
            fig = go.Figure()
            
            for idx, row in df_filtered.iterrows():
                fig.add_trace(go.Scatter(
                    x=[row['DATA EVENTO'], row['DATA EVENTO']],
                    y=[idx, idx],
                    mode='markers+text',
                    marker=dict(
                        size=15,
                        color=get_color_by_status(row['STATO']),
                        symbol='circle'
                    ),
                    text=row['NOME EVENTO'],
                    textposition='middle right',
                    hovertemplate=f"<b>{row['NOME EVENTO']}</b><br>" +
                                 f"Data: {row['DATA EVENTO'].strftime('%d/%m/%Y')}<br>" +
                                 f"Categoria: {row['CATEGORIA']}<br>" +
                                 f"Stato: {row['STATO']}<br>" +
                                 f"Priorità: {row['PRIORITÀ']}<br>" +
                                 "<extra></extra>",
                    showlegend=False
                ))
            
            fig.update_layout(
                title="Timeline Eventi",
                xaxis_title="Data",
                yaxis=dict(showticklabels=False, title=""),
                height=max(400, len(df_filtered) * 30),
                hovermode='closest'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Lista dettagliata
            st.markdown("---")
            st.subheader("📋 Dettaglio Eventi")
            for _, evento in df_filtered.iterrows():
                priority_class = f"priority-{evento['PRIORITÀ'].lower()}" if pd.notna(evento['PRIORITÀ']) else ""
                data_str = evento['DATA EVENTO'].strftime('%d/%m/%Y')
                
                st.markdown(f"""
                <div class="event-card {priority_class}">
                    <h4>{evento['NOME EVENTO']}</h4>
                    📅 <strong>{data_str}</strong><br>
                    🏷️ {evento['CATEGORIA']}<br>
                    👤 {evento['A CHI CHIEDERE']}<br>
                    📊 Stato: <strong>{evento['STATO']}</strong> | 
                    🎯 Priorità: <strong>{evento['PRIORITÀ']}</strong><br>
                    {f'📝 {evento["NOTE"]}' if pd.notna(evento['NOTE']) and evento['NOTE'] else ''}
                    {f'<br>🏷️ Tags: {evento["TAG"]}' if pd.notna(evento['TAG']) and evento['TAG'] else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nessun evento con i filtri selezionati")
    else:
        st.info("📭 Nessun evento nel database")

# ========== KANBAN BOARD ==========
elif menu_option == "📋 Kanban Board":
    st.header("Kanban Board - Vista per Stato")
    
    if len(df) > 0:
        # Filtro categoria
        filtro_cat = st.multiselect("Filtra per Categoria", CATEGORIE, default=[])
        df_kanban = df.copy()
        if filtro_cat:
            df_kanban = df_kanban[df_kanban['CATEGORIA'].isin(filtro_cat)]
        
        # Colonne per ogni stato
        cols = st.columns(len(STATI))
        
        for idx, stato in enumerate(STATI):
            with cols[idx]:
                eventi_stato = df_kanban[df_kanban['STATO'] == stato]
                
                st.markdown(f"""
                <div style='background-color: {get_color_by_status(stato)}; 
                            padding: 1rem; border-radius: 10px; text-align: center; 
                            color: white; font-weight: bold; margin-bottom: 1rem;'>
                    {stato}<br>
                    <span style='font-size: 1.5rem;'>{len(eventi_stato)}</span>
                </div>
                """, unsafe_allow_html=True)
                
                for _, evento in eventi_stato.iterrows():
                    data_str = evento['DATA EVENTO'].strftime('%d/%m')
                    priority_color = get_color_by_priority(evento['PRIORITÀ'])
                    
                    st.markdown(f"""
                    <div style='background-color: white; padding: 1rem; border-radius: 8px; 
                                margin-bottom: 0.5rem; border-left: 4px solid {priority_color};
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <strong>{evento['NOME EVENTO']}</strong><br>
                        <small>
                            📅 {data_str}<br>
                            👤 {evento['A CHI CHIEDERE']}<br>
                            🎯 {evento['PRIORITÀ']}
                        </small>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("📭 Nessun evento nel database")

# ========== TABELLA DATI ==========
elif menu_option == "📑 Tabella Dati":
    st.header("Tabella Dati Completa")
    
    if len(df) > 0:
        # Filtri avanzati
        with st.expander("🔍 Filtri Avanzati", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                filtro_cat = st.multiselect("Categoria", CATEGORIE)
            with col2:
                filtro_stato = st.multiselect("Stato", STATI)
            with col3:
                filtro_prior = st.multiselect("Priorità", PRIORITA)
            with col4:
                filtro_persona = st.multiselect(
                    "Persona",
                    df['A CHI CHIEDERE'].unique().tolist()
                )
            
            col1, col2 = st.columns(2)
            with col1:
                data_da = st.date_input("Data Da", value=None)
            with col2:
                data_a = st.date_input("Data A", value=None)
            
            search_term = st.text_input("🔍 Cerca nel nome evento o note")
        
        # Applica filtri
        df_filtered = df.copy()
        
        if filtro_cat:
            df_filtered = df_filtered[df_filtered['CATEGORIA'].isin(filtro_cat)]
        if filtro_stato:
            df_filtered = df_filtered[df_filtered['STATO'].isin(filtro_stato)]
        if filtro_prior:
            df_filtered = df_filtered[df_filtered['PRIORITÀ'].isin(filtro_prior)]
        if filtro_persona:
            df_filtered = df_filtered[df_filtered['A CHI CHIEDERE'].isin(filtro_persona)]
        if data_da:
            df_filtered = df_filtered[df_filtered['DATA EVENTO'] >= pd.to_datetime(data_da)]
        if data_a:
            df_filtered = df_filtered[df_filtered['DATA EVENTO'] <= pd.to_datetime(data_a)]
        if search_term:
            mask = (
                df_filtered['NOME EVENTO'].str.contains(search_term, case=False, na=False) |
                df_filtered['NOTE'].str.contains(search_term, case=False, na=False)
            )
            df_filtered = df_filtered[mask]
        
        # Ordina
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"📊 Visualizzazione **{len(df_filtered)}** eventi su {len(df)} totali")
        with col2:
            ordina = st.selectbox(
                "Ordina per",
                ['DATA EVENTO', 'NOME EVENTO', 'PRIORITÀ', 'STATO']
            )
        
        df_filtered = df_filtered.sort_values(by=ordina)
        
        # Mostra tabella
        st.dataframe(
            df_filtered,
            use_container_width=True,
            hide_index=True,
            column_config={
                "DATA EVENTO": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "LINK EVENTO": st.column_config.LinkColumn("Link"),
                "PRIORITÀ": st.column_config.TextColumn("Priorità"),
                "STATO": st.column_config.TextColumn("Stato")
            }
        )
        
        # Download
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                label="📥 Scarica Excel",
                data=open(EXCEL_FILE, 'rb').read(),
                file_name=f"eventi_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with col2:
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="📥 Scarica CSV",
                data=csv,
                file_name=f"eventi_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("📭 Nessun evento nel database")

# ========== NUOVO EVENTO ==========
elif menu_option == "➕ Nuovo Evento":
    st.header("Aggiungi Nuovo Evento")
    
    with st.form("nuovo_evento_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            data_evento = st.date_input("📅 Data Evento*", datetime.now())
            nome_evento = st.text_input("📝 Nome Evento*")
            categoria = st.selectbox("🏷️ Categoria*", CATEGORIE)
            stato = st.selectbox("📊 Stato*", STATI, index=0)
        
        with col2:
            link_evento = st.text_input("🔗 Link Evento")
            persona = st.text_input("👤 A Chi Chiedere*")
            priorita = st.selectbox("🎯 Priorità*", PRIORITA, index=1)
            tag = st.text_input("🏷️ Tag (separati da virgola)")
        
        note = st.text_area("📝 Note")
        
        submitted = st.form_submit_button("➕ Aggiungi Evento", use_container_width=True, type="primary")
        
        if submitted:
            if nome_evento and persona:
                nuovo_evento = {
                    'DATA EVENTO': data_evento,
                    'NOME EVENTO': nome_evento,
                    'LINK EVENTO': link_evento,
                    'A CHI CHIEDERE': persona,
                    'CATEGORIA': categoria,
                    'USER INSERIMENTO': username,
                    'TIMESTAMP INSERIMENTO': datetime.now(),
                    'USER MODIFICA': '',
                    'TIMESTAMP MODIFICA': '',
                    'STATO': stato,
                    'PRIORITÀ': priorita,
                    'NOTE': note,
                    'TAG': tag
                }
                
                df = pd.concat([df, pd.DataFrame([nuovo_evento])], ignore_index=True)
                save_data(df)
                
                st.success(f"✅ Evento '{nome_evento}' aggiunto con successo!")
                st.balloons()
                st.rerun()
            else:
                st.error("⚠️ Compila tutti i campi obbligatori (*)")

# ========== MODIFICA EVENTO ==========
elif menu_option == "✏️ Modifica Evento":
    st.header("Modifica Evento Esistente")
    
    if len(df) > 0:
        # Search e filtro
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("🔍 Cerca evento")
        with col2:
            filtro_stato_mod = st.selectbox("Stato", ['Tutti'] + STATI)
        
        # Filtra eventi
        df_search = df.copy()
        if search:
            mask = (
                df_search['NOME EVENTO'].str.contains(search, case=False, na=False) |
                df_search['A CHI CHIEDERE'].str.contains(search, case=False, na=False)
            )
            df_search = df_search[mask]
        if filtro_stato_mod != 'Tutti':
            df_search = df_search[df_search['STATO'] == filtro_stato_mod]
        
        if len(df_search) > 0:
            eventi_lista = [
                f"{row['NOME EVENTO']} - {row['DATA EVENTO'].strftime('%d/%m/%Y') if pd.notna(row['DATA EVENTO']) else 'N/A'} [{row['STATO']}]"
                for idx, row in df_search.iterrows()
            ]
            
            evento_idx = st.selectbox(
                "Seleziona Evento da Modificare",
                options=range(len(df_search)),
                format_func=lambda x: eventi_lista[x]
            )
            
            evento_selezionato = df_search.iloc[evento_idx]
            idx_originale = df_search.index[evento_idx]
            
            st.markdown("---")
            
            with st.form("modifica_evento_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    data_mod = st.date_input(
                        "📅 Data Evento*",
                        value=pd.to_datetime(evento_selezionato['DATA EVENTO'])
                    )
                    nome_mod = st.text_input(
                        "📝 Nome Evento*",
                        value=evento_selezionato['NOME EVENTO']
                    )
                    cat_mod = st.selectbox(
                        "🏷️ Categoria*",
                        CATEGORIE,
                        index=CATEGORIE.index(evento_selezionato['CATEGORIA'])
                    )
                    stato_mod = st.selectbox(
                        "📊 Stato*",
                        STATI,
                        index=STATI.index(evento_selezionato['STATO']) if pd.notna(evento_selezionato['STATO']) else 0
                    )
                
                with col2:
                    link_mod = st.text_input(
                        "🔗 Link Evento",
                        value=evento_selezionato['LINK EVENTO'] if pd.notna(evento_selezionato['LINK EVENTO']) else ""
                    )
                    persona_mod = st.text_input(
                        "👤 A Chi Chiedere*",
                        value=evento_selezionato['A CHI CHIEDERE']
                    )
                    prior_mod = st.selectbox(
                        "🎯 Priorità*",
                        PRIORITA,
                        index=PRIORITA.index(evento_selezionato['PRIORITÀ']) if pd.notna(evento_selezionato['PRIORITÀ']) else 1
                    )
                    tag_mod = st.text_input(
                        "🏷️ Tag",
                        value=evento_selezionato['TAG'] if pd.notna(evento_selezionato['TAG']) else ""
                    )
                
                note_mod = st.text_area(
                    "📝 Note",
                    value=evento_selezionato['NOTE'] if pd.notna(evento_selezionato['NOTE']) else ""
                )
                
                col_btn1, col_btn2 = st.columns([1, 1])
                
                with col_btn1:
                    submitted_mod = st.form_submit_button(
                        "💾 Salva Modifiche",
                        use_container_width=True,
                        type="primary"
                    )
                
                with col_btn2:
                    elimina = st.form_submit_button(
                        "🗑️ Elimina Evento",
                        use_container_width=True
                    )
                
                if submitted_mod:
                    if nome_mod and persona_mod:
                        df.at[idx_originale, 'DATA EVENTO'] = data_mod
                        df.at[idx_originale, 'NOME EVENTO'] = nome_mod
                        df.at[idx_originale, 'LINK EVENTO'] = link_mod
                        df.at[idx_originale, 'A CHI CHIEDERE'] = persona_mod
                        df.at[idx_originale, 'CATEGORIA'] = cat_mod
                        df.at[idx_originale, 'STATO'] = stato_mod
                        df.at[idx_originale, 'PRIORITÀ'] = prior_mod
                        df.at[idx_originale, 'NOTE'] = note_mod
                        df.at[idx_originale, 'TAG'] = tag_mod
                        df.at[idx_originale, 'USER MODIFICA'] = username
                        df.at[idx_originale, 'TIMESTAMP MODIFICA'] = datetime.now()
                        
                        save_data(df)
                        st.success("✅ Evento modificato con successo!")
                        st.rerun()
                    else:
                        st.error("⚠️ Compila tutti i campi obbligatori (*)")
                
                if elimina:
                    df = df.drop(idx_originale).reset_index(drop=True)
                    save_data(df)
                    st.success("✅ Evento eliminato con successo!")
                    st.rerun()
            
            # Metadati
            st.markdown("---")
            st.subheader("ℹ️ Metadati Evento")
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Inserito da:** {evento_selezionato['USER INSERIMENTO']}")
                if pd.notna(evento_selezionato['TIMESTAMP INSERIMENTO']):
                    st.info(f"**Inserito il:** {evento_selezionato['TIMESTAMP INSERIMENTO']}")
            with col2:
                if pd.notna(evento_selezionato['USER MODIFICA']) and evento_selezionato['USER MODIFICA']:
                    st.info(f"**Modificato da:** {evento_selezionato['USER MODIFICA']}")
                    if pd.notna(evento_selezionato['TIMESTAMP MODIFICA']):
                        st.info(f"**Modificato il:** {evento_selezionato['TIMESTAMP MODIFICA']}")
                else:
                    st.info("**Nessuna modifica registrata**")
        else:
            st.warning("Nessun evento trovato con i criteri di ricerca")
    else:
        st.info("📭 Non ci sono eventi da modificare")

# ========== ANALYTICS ==========
elif menu_option == "📈 Analytics":
    st.header("Analytics Avanzate")
    
    if len(df) > 0:
        tab1, tab2, tab3 = st.tabs(["📊 Statistiche", "👥 Persone", "🏷️ Categorie"])
        
        with tab1:
            st.subheader("Statistiche Generali")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📌 Totale Eventi", len(df))
            with col2:
                media_eventi_mese = len(df) / df['DATA EVENTO'].dt.to_period('M').nunique()
                st.metric("📅 Media/Mese", f"{media_eventi_mese:.1f}")
            with col3:
                prossimi_7gg = len(df[
                    (df['DATA EVENTO'] >= datetime.now()) &
                    (df['DATA EVENTO'] <= datetime.now() + timedelta(days=7))
                ])
                st.metric("🔜 Prossimi 7gg", prossimi_7gg)
            with col4:
                in_ritardo = len(df[
                    (df['DATA EVENTO'] < datetime.now()) &
                    (df['STATO'].isin(['Pianificato', 'In Corso']))
                ])
                st.metric("⚠️ In Ritardo", in_ritardo)
            
            st.markdown("---")
            
            # Matrice Priorità vs Stato
            st.subheader("🎯 Matrice Priorità vs Stato")
            pivot_table = pd.crosstab(df['PRIORITÀ'], df['STATO'])
            
            fig_heatmap = px.imshow(
                pivot_table,
                labels=dict(x="Stato", y="Priorità", color="Numero Eventi"),
                x=pivot_table.columns,
                y=pivot_table.index,
                color_continuous_scale='Blues',
                text_auto=True
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Trend temporale
            st.subheader("📈 Trend Eventi nel Tempo")
            df_trend = df.copy()
            df_trend['Settimana'] = df_trend['DATA EVENTO'].dt.to_period('W').astype(str)
            trend_data = df_trend.groupby(['Settimana', 'STATO']).size().reset_index(name='Count')
            
            fig_trend = px.line(
                trend_data,
                x='Settimana',
                y='Count',
                color='STATO',
                markers=True,
                title="Eventi per Settimana"
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with tab2:
            st.subheader("👥 Analisi per Persona")
            
            # Top contributori
            persone_stats = df.groupby('A CHI CHIEDERE').agg({
                'NOME EVENTO': 'count',
                'PRIORITÀ': lambda x: (x == 'Alta').sum(),
                'STATO': lambda x: (x == 'Completato').sum()
            }).reset_index()
            persone_stats.columns = ['Persona', 'Totale Eventi', 'Alta Priorità', 'Completati']
            persone_stats = persone_stats.sort_values('Totale Eventi', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_persone_total = px.bar(
                    persone_stats.head(10),
                    x='Persona',
                    y='Totale Eventi',
                    title="Top 10 Persone per Numero Eventi",
                    color='Totale Eventi',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig_persone_total, use_container_width=True)
            
            with col2:
                fig_persone_comp = px.bar(
                    persone_stats.head(10),
                    x='Persona',
                    y='Completati',
                    title="Top 10 Persone per Eventi Completati",
                    color='Completati',
                    color_continuous_scale='Greens'
                )
                st.plotly_chart(fig_persone_comp, use_container_width=True)
            
            st.dataframe(persone_stats, use_container_width=True, hide_index=True)
        
        with tab3:
            st.subheader("🏷️ Analisi per Categoria")
            
            cat_stats = df.groupby('CATEGORIA').agg({
                'NOME EVENTO': 'count',
                'STATO': lambda x: (x == 'Completato').sum()
            }).reset_index()
            cat_stats.columns = ['Categoria', 'Totale', 'Completati']
            cat_stats['% Completamento'] = (cat_stats['Completati'] / cat_stats['Totale'] * 100).round(1)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_cat_dist = px.pie(
                    cat_stats,
                    values='Totale',
                    names='Categoria',
                    title="Distribuzione Eventi per Categoria"
                )
                st.plotly_chart(fig_cat_dist, use_container_width=True)
            
            with col2:
                fig_cat_comp = px.bar(
                    cat_stats,
                    x='Categoria',
                    y='% Completamento',
                    title="% Completamento per Categoria",
                    color='% Completamento',
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig_cat_comp, use_container_width=True)
            
            st.dataframe(cat_stats, use_container_width=True, hide_index=True)
            
            # Tag cloud
            st.subheader("🏷️ Tag Cloud")
            all_tags = []
            for tags in df['TAG'].dropna():
                all_tags.extend([t.strip() for t in str(tags).split(',')])
            
            if all_tags:
                tag_counts = Counter(all_tags)
                tag_df = pd.DataFrame(tag_counts.items(), columns=['Tag', 'Frequenza'])
                tag_df = tag_df.sort_values('Frequenza', ascending=False)
                
                fig_tags = px.bar(
                    tag_df.head(20),
                    x='Tag',
                    y='Frequenza',
                    title="Top 20 Tag più Utilizzati",
                    color='Frequenza',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_tags, use_container_width=True)
    else:
        st.info("📭 Nessun evento nel database per generare analytics")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(
        "<div style='text-align: center; color: gray;'>📅 Sistema Gestione Eventi Pro v2.0 - Powered by Streamlit</div>",
        unsafe_allow_html=True
    )
