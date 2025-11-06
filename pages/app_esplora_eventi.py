import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from collections import Counter

st.set_page_config(
    page_title="Esplora Eventi",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
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
</style>
""", unsafe_allow_html=True)

EXCEL_FILE = "gestione_eventi.xlsx"

CATEGORIE = [
    'EVENTI sociali/politici/economici',
    'EVENTI delle organizzazioni',
    'EVENTI che interessano a logotel',
    'EVENTI di logotel che farà'
]

@st.cache_data(ttl=1)
def load_data():
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        if 'DATA EVENTO' in df.columns:
            df['DATA EVENTO'] = pd.to_datetime(df['DATA EVENTO'], errors='coerce', dayfirst=True)
        if 'TIMESTAMP INSERIMENTO' in df.columns:
            df['TIMESTAMP INSERIMENTO'] = pd.to_datetime(df['TIMESTAMP INSERIMENTO'], errors='coerce')
        if 'TIMESTAMP MODIFICA' in df.columns:
            df['TIMESTAMP MODIFICA'] = pd.to_datetime(df['TIMESTAMP MODIFICA'], errors='coerce')
        return df
    return pd.DataFrame()

def save_data(df):
    df.to_excel(EXCEL_FILE, index=False)
    st.cache_data.clear()

# Sidebar
with st.sidebar:
    st.markdown("### 🔍 Esplora Eventi")
    st.markdown("*Scopri affinità e potenzialità*")
    st.markdown("---")
    
    username = st.text_input("👤 Utente", value="admin", key="username")
    st.markdown("---")
    
    menu_option = st.radio(
        "Vista",
        ["🗓️ Timeline", "🏷️ Per Categoria", "👥 Per Contatto", 
         "🔍 Cerca & Filtra", "➕ Nuovo Evento", "📊 Insights"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    df = load_data()
    if len(df) > 0:
        st.metric("📌 Totale Eventi", len(df))
        st.metric("📅 Prossimi 30gg", len(df[
            (df['DATA EVENTO'] >= datetime.now()) &
            (df['DATA EVENTO'] <= datetime.now() + timedelta(days=30))
        ]))

st.markdown('<div class="main-header">🔍 Esplora Eventi</div>', unsafe_allow_html=True)

# ========== TIMELINE ==========
if menu_option == "🗓️ Timeline":
    st.header("Timeline Cronologica")
    
    if len(df) > 0:
        col1, col2 = st.columns([2, 1])
        with col1:
            filtro_cat = st.multiselect("Filtra per Categoria", CATEGORIE, key="tl_cat")
        with col2:
            periodo = st.selectbox("Periodo", ["Tutti", "Passati", "Futuri", "Questo Mese", "Prossimi 3 Mesi"])
        
        df_filtered = df.copy()
        
        # Filtro categoria
        if filtro_cat:
            df_filtered = df_filtered[df_filtered['CATEGORIA'].isin(filtro_cat)]
        
        # Filtro periodo
        now = datetime.now()
        if periodo == "Passati":
            df_filtered = df_filtered[df_filtered['DATA EVENTO'] < now]
        elif periodo == "Futuri":
            df_filtered = df_filtered[df_filtered['DATA EVENTO'] >= now]
        elif periodo == "Questo Mese":
            df_filtered = df_filtered[
                (df_filtered['DATA EVENTO'].dt.month == now.month) &
                (df_filtered['DATA EVENTO'].dt.year == now.year)
            ]
        elif periodo == "Prossimi 3 Mesi":
            df_filtered = df_filtered[
                (df_filtered['DATA EVENTO'] >= now) &
                (df_filtered['DATA EVENTO'] <= now + timedelta(days=90))
            ]
        
        df_filtered = df_filtered.sort_values('DATA EVENTO')
        
        st.info(f"📊 **{len(df_filtered)} eventi** visualizzati")
        
        if len(df_filtered) > 0:
            # Timeline grafico
            fig = go.Figure()
            
            colors_cat = {
                'EVENTI sociali/politici/economici': '#e74c3c',
                'EVENTI delle organizzazioni': '#3498db',
                'EVENTI che interessano a logotel': '#f39c12',
                'EVENTI di logotel che farà': '#2ecc71'
            }
            
            for cat in df_filtered['CATEGORIA'].unique():
                df_cat = df_filtered[df_filtered['CATEGORIA'] == cat]
                fig.add_trace(go.Scatter(
                    x=df_cat['DATA EVENTO'],
                    y=[cat] * len(df_cat),
                    mode='markers',
                    marker=dict(size=12, color=colors_cat.get(cat, '#95a5a6')),
                    text=df_cat['NOME EVENTO'],
                    hovertemplate='<b>%{text}</b><br>%{x}<extra></extra>',
                    name=cat[:30] + "..."
                ))
            
            fig.update_layout(
                title="Eventi nel Tempo",
                xaxis_title="Data",
                yaxis_title="",
                height=400,
                hovermode='closest',
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Lista dettagliata
            st.markdown("---")
            st.subheader("📋 Dettaglio Eventi")
            
            df_filtered_sorted = df_filtered.sort_values(by='DATA EVENTO', ascending=False)

            for _, evento in df_filtered_sorted.iterrows():
                data_str = evento['DATA EVENTO'].strftime('%d/%m/%Y') if pd.notna(evento['DATA EVENTO']) else 'N/A'
                
                with st.expander(f"📅 {data_str} - {evento['NOME EVENTO']}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Categoria:** {evento['CATEGORIA']}")
                        st.write(f"**Contatto:** {evento['A CHI CHIEDERE']}")
                        if pd.notna(evento['LINK EVENTO']) and evento['LINK EVENTO']:
                            st.write(f"**Link:** [{evento['LINK EVENTO']}]({evento['LINK EVENTO']})")
                    with col2:
                        if 'NOTE' in evento and pd.notna(evento['NOTE']) and evento['NOTE']:
                            st.write(f"**Note:** {evento['NOTE']}")
                        if 'TAG' in evento and pd.notna(evento['TAG']) and evento['TAG']:
                            st.write(f"**Tag:** {evento['TAG']}")
        else:
            st.warning("Nessun evento trovato con i filtri selezionati")
    else:
        st.info("📭 Nessun evento nel database")

# ========== PER CATEGORIA ==========
elif menu_option == "🏷️ Per Categoria":
    st.header("Esplora per Categoria")
    
    if len(df) > 0:
        # Overview categorie
        st.subheader("📊 Distribuzione Categorie")
        cat_counts = df['CATEGORIA'].value_counts()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            fig_pie = px.pie(
                values=cat_counts.values,
                names=cat_counts.index,
                title="Proporzione Eventi",
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            fig_bar = px.bar(
                x=cat_counts.values,
                y=cat_counts.index,
                orientation='h',
                title="Numero Eventi per Categoria",
                labels={'x': 'Numero Eventi', 'y': ''}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("---")
        
        # Esplora ogni categoria
        st.subheader("🔍 Esplora Categoria")
        categoria_sel = st.selectbox("Seleziona Categoria", CATEGORIE)
        
        df_cat = df[df['CATEGORIA'] == categoria_sel].sort_values('DATA EVENTO')
        
        if len(df_cat) > 0:
            st.info(f"**{len(df_cat)} eventi** in questa categoria")
            
            # Insights categoria
            col1, col2, col3 = st.columns(3)
            with col1:
                prossimi = len(df_cat[df_cat['DATA EVENTO'] >= datetime.now()])
                st.metric("🔜 Prossimi Eventi", prossimi)
            with col2:
                persone = df_cat['A CHI CHIEDERE'].nunique()
                st.metric("👥 Contatti Coinvolti", persone)
            with col3:
                if len(df_cat) > 0:
                    data_min = df_cat['DATA EVENTO'].min()
                    data_max = df_cat['DATA EVENTO'].max()
                    giorni = (data_max - data_min).days
                    st.metric("📅 Arco Temporale", f"{giorni} giorni")
            
            # Top contatti per questa categoria
            st.markdown("#### 👥 Top Contatti")
            top_contatti = df_cat['A CHI CHIEDERE'].value_counts().head(5)
            fig_contatti = px.bar(
                x=top_contatti.values,
                y=top_contatti.index,
                orientation='h',
                labels={'x': 'Numero Eventi', 'y': 'Contatto'}
            )
            st.plotly_chart(fig_contatti, use_container_width=True)
            
            # Lista eventi
            st.markdown("#### 📋 Eventi")
            for _, evento in df_cat.iterrows():
                data_str = evento['DATA EVENTO'].strftime('%d/%m/%Y') if pd.notna(evento['DATA EVENTO']) else 'N/A'
                st.markdown(f"""
                <div class="event-card">
                    <strong>{evento['NOME EVENTO']}</strong><br>
                    📅 {data_str} | 👤 {evento['A CHI CHIEDERE']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Nessun evento in questa categoria")
    else:
        st.info("📭 Nessun evento nel database")

# ========== PER CONTATTO ==========
elif menu_option == "👥 Per Contatto":
    st.header("Esplora per Contatto")
    
    if len(df) > 0:
        # Top contatti
        st.subheader("📊 Top Contatti")
        contatti_counts = df['A CHI CHIEDERE'].value_counts().head(15)
        
        fig = px.bar(
            x=contatti_counts.values,
            y=contatti_counts.index,
            orientation='h',
            title="Numero Eventi per Contatto",
            labels={'x': 'Numero Eventi', 'y': 'Contatto'},
            color=contatti_counts.values,
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Seleziona contatto
        st.subheader("🔍 Esplora Contatto")
        contatto_sel = st.selectbox("Seleziona Contatto", sorted(df['A CHI CHIEDERE'].unique()))
        
        df_contatto = df[df['A CHI CHIEDERE'] == contatto_sel].sort_values('DATA EVENTO')
        
        if len(df_contatto) > 0:
            st.info(f"**{len(df_contatto)} eventi** con questo contatto")
            
            # Insights contatto
            col1, col2, col3 = st.columns(3)
            with col1:
                categorie_coinvolte = df_contatto['CATEGORIA'].nunique()
                st.metric("🏷️ Categorie Coinvolte", categorie_coinvolte)
            with col2:
                prossimi = len(df_contatto[df_contatto['DATA EVENTO'] >= datetime.now()])
                st.metric("🔜 Prossimi Eventi", prossimi)
            with col3:
                passati = len(df_contatto[df_contatto['DATA EVENTO'] < datetime.now()])
                st.metric("✅ Eventi Passati", passati)
            
            # Distribuzione categorie per questo contatto
            st.markdown("#### 🏷️ Categorie per questo Contatto")
            cat_dist = df_contatto['CATEGORIA'].value_counts()
            fig_cat = px.pie(
                values=cat_dist.values,
                names=cat_dist.index,
                title=f"Categorie di {contatto_sel}"
            )
            st.plotly_chart(fig_cat, use_container_width=True)
            
            # Timeline eventi
            st.markdown("#### 📅 Timeline Eventi")
            fig_timeline = px.scatter(
                df_contatto,
                x='DATA EVENTO',
                y='CATEGORIA',
                text='NOME EVENTO',
                title=f"Eventi di {contatto_sel} nel tempo"
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Lista eventi
            st.markdown("#### 📋 Tutti gli Eventi")
            for _, evento in df_contatto.iterrows():
                data_str = evento['DATA EVENTO'].strftime('%d/%m/%Y') if pd.notna(evento['DATA EVENTO']) else 'N/A'
                st.markdown(f"""
                <div class="event-card">
                    <strong>{evento['NOME EVENTO']}</strong><br>
                    📅 {data_str} | 🏷️ {evento['CATEGORIA']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Nessun evento per questo contatto")
    else:
        st.info("📭 Nessun evento nel database")

# ========== CERCA & FILTRA ==========
elif menu_option == "🔍 Cerca & Filtra":
    st.header("Cerca e Filtra Eventi")
    
    if len(df) > 0:
        # Filtri
        with st.expander("🔧 Filtri Avanzati", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search_term = st.text_input("🔍 Cerca nel nome")
                filtro_cat = st.multiselect("Categoria", CATEGORIE)
            
            with col2:
                filtro_persona = st.multiselect(
                    "Contatto",
                    sorted(df['A CHI CHIEDERE'].unique())
                )
                data_da = st.date_input("Data Da", value=None)
            
            with col3:
                if 'TAG' in df.columns:
                    # Estrai tutti i tag unici
                    all_tags = set()
                    for tags in df['TAG'].dropna():
                        all_tags.update([t.strip() for t in str(tags).split(',')])
                    if all_tags:
                        filtro_tag = st.multiselect("Tag", sorted(all_tags))
                    else:
                        filtro_tag = []
                else:
                    filtro_tag = []
                
                data_a = st.date_input("Data A", value=None)
        
        # Applica filtri
        df_filtered = df.copy()
        
        if search_term:
            mask = df_filtered['NOME EVENTO'].str.contains(search_term, case=False, na=False)
            if 'NOTE' in df_filtered.columns:
                mask |= df_filtered['NOTE'].str.contains(search_term, case=False, na=False)
            df_filtered = df_filtered[mask]
        
        if filtro_cat:
            df_filtered = df_filtered[df_filtered['CATEGORIA'].isin(filtro_cat)]
        
        if filtro_persona:
            df_filtered = df_filtered[df_filtered['A CHI CHIEDERE'].isin(filtro_persona)]
        
        if filtro_tag and 'TAG' in df.columns:
            mask = df_filtered['TAG'].apply(
                lambda x: any(tag in str(x) for tag in filtro_tag) if pd.notna(x) else False
            )
            df_filtered = df_filtered[mask]
        
        if data_da:
            df_filtered = df_filtered[df_filtered['DATA EVENTO'] >= pd.to_datetime(data_da)]
        
        if data_a:
            df_filtered = df_filtered[df_filtered['DATA EVENTO'] <= pd.to_datetime(data_a)]
        
        # Risultati
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"📊 Risultati: {len(df_filtered)} eventi")
        with col2:
            ordina = st.selectbox("Ordina", ['DATA EVENTO', 'NOME EVENTO', 'CATEGORIA'])
        
        df_filtered = df_filtered.sort_values(by=ordina)
        
        if len(df_filtered) > 0:
            # Tabella
            st.dataframe(
                df_filtered[['DATA EVENTO', 'NOME EVENTO', 'CATEGORIA', 'A CHI CHIEDERE']],
                use_container_width=True,
                hide_index=True
            )
            
            # Export
            col1, col2 = st.columns(2)
            with col1:
                csv = df_filtered.to_csv(index=False)
                st.download_button(
                    "📥 Scarica CSV",
                    csv,
                    f"eventi_filtrati_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
            with col2:
                st.download_button(
                    "📥 Scarica Excel",
                    open(EXCEL_FILE, 'rb').read(),
                    f"eventi_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("Nessun evento trovato con i filtri selezionati")
    else:
        st.info("📭 Nessun evento nel database")

# ========== NUOVO EVENTO ==========
elif menu_option == "➕ Nuovo Evento":
    st.header("Registra Nuovo Evento")
    
    with st.form("nuovo_evento", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("📝 Nome Evento*", placeholder="Es: Conferenza AI 2025")
            data = st.date_input("📅 Data Evento*", datetime.now())
            categoria = st.selectbox("🏷️ Categoria*", CATEGORIE)
        
        with col2:
            persona = st.text_input("👤 Contatto*", placeholder="Nome referente")
            link = st.text_input("🔗 Link", placeholder="https://...")
            tag = st.text_input("🏷️ Tag", placeholder="tech, AI, formazione (separati da virgola)")
        
        note = st.text_area("📝 Note", placeholder="Descrizione, informazioni aggiuntive...")
        
        submitted = st.form_submit_button("➕ Aggiungi Evento", type="primary", use_container_width=True)
        
        if submitted:
            if nome and persona:
                nuovo = {
                    'DATA EVENTO': data,
                    'NOME EVENTO': nome,
                    'LINK EVENTO': link,
                    'A CHI CHIEDERE': persona,
                    'CATEGORIA': categoria,
                    'USER INSERIMENTO': username,
                    'TIMESTAMP INSERIMENTO': datetime.now(),
                    'USER MODIFICA': '',
                    'TIMESTAMP MODIFICA': ''
                }
                
                if 'NOTE' in df.columns:
                    nuovo['NOTE'] = note
                if 'TAG' in df.columns:
                    nuovo['TAG'] = tag
                
                df = pd.concat([df, pd.DataFrame([nuovo])], ignore_index=True)
                save_data(df)
                
                st.success(f"✅ Evento '{nome}' registrato con successo!")
                st.balloons()
                st.rerun()
            else:
                st.error("⚠️ Compila i campi obbligatori (*)")

# ========== INSIGHTS ==========
elif menu_option == "📊 Insights":
    st.header("Insights e Affinità")
    
    if len(df) > 0:
        # Insights box
        st.markdown("""
        <div class="insight-box">
            <h3>🎯 Cosa scoprire</h3>
            <p>Esplora pattern, affinità e potenzialità nei tuoi eventi</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["📈 Trend", "🤝 Affinità", "💡 Potenzialità"])
        
        with tab1:
            st.subheader("📈 Trend Temporali")
            
            # Eventi per mese
            df['Mese'] = df['DATA EVENTO'].dt.to_period('M').astype(str)
            eventi_mese = df.groupby('Mese').size().reset_index(name='Numero Eventi')
            
            fig = px.line(
                eventi_mese,
                x='Mese',
                y='Numero Eventi',
                markers=True,
                title="Evoluzione Eventi nel Tempo"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Distribuzione per giorno settimana
            df['Giorno'] = df['DATA EVENTO'].dt.day_name()
            giorni_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            giorni_it = {'Monday': 'Lunedì', 'Tuesday': 'Martedì', 'Wednesday': 'Mercoledì', 
                        'Thursday': 'Giovedì', 'Friday': 'Venerdì', 'Saturday': 'Sabato', 'Sunday': 'Domenica'}
            
            giorno_counts = df['Giorno'].value_counts()
            fig_giorni = px.bar(
                x=[giorni_it[g] for g in giorni_order if g in giorno_counts.index],
                y=[giorno_counts[g] for g in giorni_order if g in giorno_counts.index],
                title="Eventi per Giorno della Settimana",
                labels={'x': 'Giorno', 'y': 'Numero Eventi'}
            )
            st.plotly_chart(fig_giorni, use_container_width=True)
        
        with tab2:
            st.subheader("🤝 Affinità e Relazioni")
            
            # Matrice contatti x categorie
            st.markdown("#### Contatti più Attivi per Categoria")
            pivot = pd.crosstab(df['A CHI CHIEDERE'], df['CATEGORIA'])
            
            # Top 10 contatti
            top_contatti = df['A CHI CHIEDERE'].value_counts().head(10).index
            pivot_top = pivot.loc[top_contatti]
            
            fig_heatmap = px.imshow(
                pivot_top,
                labels=dict(x="Categoria", y="Contatto", color="Eventi"),
                x=pivot_top.columns,
                y=pivot_top.index,
                color_continuous_scale='Blues',
                text_auto=True,
                aspect='auto'
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Contatti che condividono categorie
            st.markdown("#### 🔗 Possibili Sinergie")
            st.info("Contatti che operano nelle stesse categorie potrebbero avere interessi comuni")
            
            for cat in CATEGORIE:
                df_cat = df[df['CATEGORIA'] == cat]
                contatti = df_cat['A CHI CHIEDERE'].unique()
                if len(contatti) > 1:
                    st.markdown(f"**{cat}:**")
                    st.write(", ".join(contatti[:10]))
        
        with tab3:
            st.subheader("💡 Potenzialità")
            
            # Categorie con più momentum
            st.markdown("#### 🚀 Categorie in Crescita")
            
            # Eventi ultimi 3 mesi vs precedenti
            now = datetime.now()
            tre_mesi_fa = now - timedelta(days=90)
            sei_mesi_fa = now - timedelta(days=180)
            
            df_recenti = df[(df['DATA EVENTO'] >= tre_mesi_fa) & (df['DATA EVENTO'] <= now)]
            df_precedenti = df[(df['DATA EVENTO'] >= sei_mesi_fa) & (df['DATA EVENTO'] < tre_mesi_fa)]
            
            if len(df_recenti) > 0 and len(df_precedenti) > 0:
                recenti_cat = df_recenti['CATEGORIA'].value_counts()
                precedenti_cat = df_precedenti['CATEGORIA'].value_counts()
                
                for cat in CATEGORIE:
                    rec = recenti_cat.get(cat, 0)
                    prec = precedenti_cat.get(cat, 0)
                    if prec > 0:
                        crescita = ((rec - prec) / prec * 100)
                        if crescita > 0:
                            st.metric(cat, f"{rec} eventi", f"+{crescita:.0f}% vs 3 mesi fa")
            
            # Gap da esplorare
            st.markdown("#### 🎯 Opportunità")
            
            # Contatti con pochi eventi
            contatti_counts = df['A CHI CHIEDERE'].value_counts()
            contatti_poco_attivi = contatti_counts[contatti_counts <= 2]
            
            if len(contatti_poco_attivi) > 0:
                st.info(f"**{len(contatti_poco_attivi)} contatti** hanno 1-2 eventi. Potenziale per approfondire le relazioni!")
            
            # Categorie sottorappresentate
            cat_counts = df['CATEGORIA'].value_counts()
            media = cat_counts.mean()
            cat_sotto = cat_counts[cat_counts < media]
            
            if len(cat_sotto) > 0:
                st.warning("**Categorie con meno eventi della media:**")
                for cat, count in cat_sotto.items():
                    st.write(f"- {cat}: {count} eventi (media: {media:.0f})")
            
            # Tag più usati
            if 'TAG' in df.columns:
                st.markdown("#### 🏷️ Tag Emergenti")
                all_tags = []
                for tags in df['TAG'].dropna():
                    all_tags.extend([t.strip() for t in str(tags).split(',')])
                
                if all_tags:
                    tag_counts = Counter(all_tags).most_common(10)
                    fig_tags = px.bar(
                        x=[t[1] for t in tag_counts],
                        y=[t[0] for t in tag_counts],
                        orientation='h',
                        title="Top 10 Tag",
                        labels={'x': 'Frequenza', 'y': 'Tag'}
                    )
                    st.plotly_chart(fig_tags, use_container_width=True)
    else:
        st.info("📭 Nessun evento nel database per generare insights")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>🔍 Esplora Eventi </div>",
    unsafe_allow_html=True
)
