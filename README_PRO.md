# 📅 Sistema Gestione Eventi PRO v2.0

Sistema professionale completo per la gestione eventi con interfaccia web Streamlit ultra-potenziata.

## 🚀 Funzionalità Complete

### ✨ 8 Viste Specializzate

#### 1. 📊 **Dashboard**
- KPI cards con metriche chiave in tempo reale
- Grafici interattivi Plotly:
  - Eventi per categoria (pie chart)
  - Distribuzione stati (bar chart colorato)
  - Timeline mensile (line chart)
  - Priorità (bar chart)
  - Top contatti (horizontal bar)
- Statistiche:
  - Totale eventi
  - Prossimi eventi
  - Eventi del mese
  - Alta priorità
  - % completamento

#### 2. 📅 **Calendario**
- Vista mensile navigabile
- Selezione mese interattiva
- Eventi raggruppati per giorno
- Card eventi espandibili con:
  - Nome evento
  - Categoria
  - Persona di riferimento
  - Stato e priorità
- Conteggio eventi per mese

#### 3. ⏱️ **Timeline**
- Vista cronologica completa
- Timeline Gantt interattiva
- Filtri multipli:
  - Categoria
  - Stato
  - Priorità
- Marker colorati per stato
- Hover con dettagli completi
- Lista dettagliata con card colorate

#### 4. 📋 **Kanban Board**
- 4 colonne per stato (Pianificato, In Corso, Completato, Annullato)
- Card drag-and-drop visual
- Colori per priorità
- Filtro per categoria
- Conteggio per colonna

#### 5. 📑 **Tabella Dati**
- Tabella completa interattiva
- Filtri avanzati:
  - Categoria (multi-select)
  - Stato (multi-select)
  - Priorità (multi-select)
  - Persona (multi-select)
  - Range date (da - a)
  - Ricerca full-text (nome + note)
- Ordinamento personalizzabile
- Export multipli:
  - Excel (.xlsx)
  - CSV (.csv)
- Conteggio eventi filtrati

#### 6. ➕ **Nuovo Evento**
- Form completo con validazione
- Campi:
  - Data evento
  - Nome evento
  - Link (opzionale)
  - Persona di riferimento
  - Categoria (dropdown)
  - Stato (dropdown)
  - Priorità (dropdown)
  - Tag (separati da virgola)
  - Note (textarea)
- Salvataggio automatico metadati:
  - Username inserimento
  - Timestamp inserimento
- Feedback visivo (success + balloons)

#### 7. ✏️ **Modifica Evento**
- Ricerca eventi avanzata
- Filtro per stato
- Selezione evento da dropdown
- Form pre-compilato
- Modifica tutti i campi
- Eliminazione evento
- Visualizzazione metadati completi:
  - Chi e quando ha inserito
  - Chi e quando ha modificato
- Aggiornamento automatico timestamp modifica

#### 8. 📈 **Analytics**
- **Tab Statistiche:**
  - KPI cards (totale, media/mese, prossimi 7gg, in ritardo)
  - Matrice priorità vs stato (heatmap)
  - Trend eventi nel tempo (line chart per settimana)
  
- **Tab Persone:**
  - Top 10 persone per numero eventi
  - Top 10 persone per eventi completati
  - Tabella dettagliata con:
    - Totale eventi
    - Eventi alta priorità
    - Eventi completati
  
- **Tab Categorie:**
  - Distribuzione eventi (pie chart)
  - % completamento per categoria
  - Tag cloud (top 20 tag più usati)
  - Statistiche complete per categoria

### 📊 Dati e Struttura

**Colonne Excel (13 totali):**
1. DATA EVENTO - Data dell'evento
2. NOME EVENTO - Nome descrittivo
3. LINK EVENTO - URL riferimento
4. A CHI CHIEDERE - Contatto
5. CATEGORIA - 4 opzioni predefinite
6. USER INSERIMENTO - Chi ha creato ⭐
7. TIMESTAMP INSERIMENTO - Quando creato ⭐
8. USER MODIFICA - Chi ha modificato ⭐
9. TIMESTAMP MODIFICA - Quando modificato ⭐
10. STATO - Pianificato/In Corso/Completato/Annullato ⭐
11. PRIORITÀ - Alta/Media/Bassa ⭐
12. NOTE - Descrizione dettagliata ⭐
13. TAG - Tag separati da virgola ⭐

**Dati Inclusi:**
- ✅ 50 righe di eventi random
- ✅ Tutti i campi popolati con dati realistici
- ✅ Date distribuite nei prossimi 6 mesi
- ✅ Mix di stati e priorità
- ✅ Tag e note di esempio

### 🎨 UI/UX Features

- **Design professionale:**
  - Gradient headers
  - Card colorate per priorità
  - Icone intuitive
  - Colori semantici per stati
  
- **Interattività:**
  - Grafici Plotly interattivi (zoom, pan, hover)
  - Filtri real-time
  - Form validation
  - Loading states
  
- **Responsive:**
  - Layout wide ottimizzato
  - Colonne adattive
  - Sidebar collassabile
  
- **User-friendly:**
  - Quick stats in sidebar
  - Tooltips e help text
  - Feedback visivo su ogni azione
  - Error handling

### 🔧 Tecnologie Utilizzate

- **Streamlit** - Framework web app
- **Pandas** - Data manipulation
- **Plotly** - Grafici interattivi
- **OpenPyXL** - Excel I/O
- **Python 3.x** - Backend logic

## 🚀 Come Avviare

### Metodo 1 - Comando diretto
```bash
streamlit run app_eventi_pro.py
```

### Metodo 2 - Script rapido
```bash
chmod +x avvia_app_pro.sh
./avvia_app_pro.sh
```

L'applicazione si aprirà automaticamente nel browser su `http://localhost:8501`

## 📋 Requisiti

```bash
pip install streamlit pandas plotly openpyxl --break-system-packages
```

## 💡 Tips & Tricks

### Filtri Combinati
Usa più filtri insieme per analisi precise:
- Categoria + Stato + Priorità
- Date range + Persona
- Ricerca full-text + Filtri

### Export Personalizzati
1. Applica i filtri desiderati
2. Usa "Scarica Excel" o "Scarica CSV"
3. Il file conterrà solo i dati filtrati

### Ricerca Avanzata
La ricerca full-text cerca in:
- Nome evento
- Note/descrizioni
Usa parole chiave per trovare rapidamente eventi specifici

### Metadati Automatici
Non preoccuparti di inserire username e timestamp:
- Si salvano automaticamente all'inserimento
- Si aggiornano automaticamente alla modifica
- Vedi sempre chi ha fatto cosa e quando

### Tag Efficaci
Usa tag per categorizzare ulteriormente:
- Separa con virgole: "strategico, Q1, cliente-vip"
- Analizza i tag più usati in Analytics
- Usa tag consistenti per migliore analisi

## 🎯 Casi d'Uso

### 1. Planning Trimestrale
- Vista Calendario → Seleziona mesi Q1
- Dashboard → Analizza distribuzione
- Kanban → Gestisci stati

### 2. Follow-up Alta Priorità
- Tabella Dati → Filtra Priorità = Alta + Stato = In Corso
- Export → Condividi con team
- Modifica → Aggiorna stati

### 3. Report Mensile
- Analytics → Tab Statistiche
- Dashboard → Screenshot grafici
- Export → Dati per report

### 4. Gestione Team
- Analytics → Tab Persone
- Vedi carico lavoro per persona
- Riassegna eventi se necessario

### 5. Analisi Trend
- Timeline → Vista cronologica
- Analytics → Trend nel tempo
- Dashboard → KPI evolutivi

## 🔐 Sicurezza

- Dati salvati localmente in Excel
- Nessun cloud storage obbligatorio
- Username tracking per audit trail
- Timestamp completi per tracciabilità

## 📁 Struttura File

```
├── gestione_eventi.xlsx          # Database eventi (13 colonne)
├── app_eventi_pro.py             # Applicazione Streamlit Pro
├── README_PRO.md                 # Questa guida
└── avvia_app_pro.sh              # Script avvio rapido
```

## 🆘 Troubleshooting

**Problema:** App non si avvia
**Soluzione:** Verifica che tutte le librerie siano installate
```bash
pip install streamlit pandas plotly openpyxl --break-system-packages
```

**Problema:** Dati non si salvano
**Soluzione:** Verifica permessi sul file gestione_eventi.xlsx

**Problema:** Grafici non interattivi
**Soluzione:** Aggiorna Plotly all'ultima versione
```bash
pip install --upgrade plotly --break-system-packages
```

**Problema:** Date non visualizzate correttamente
**Soluzione:** Il formato è DD/MM/YYYY - controlla i dati in Excel

## 🔄 Aggiornamenti Futuri

Possibili estensioni:
- [ ] Notifiche email automatiche
- [ ] Integrazione Google Calendar
- [ ] Export PDF report
- [ ] Dashboard customizzabili
- [ ] Gestione allegati
- [ ] Commenti collaborativi
- [ ] Mobile app companion

## 📞 Supporto

Per problemi o domande:
1. Controlla questa guida
2. Verifica i requisiti
3. Controlla i log di Streamlit

---

**Powered by Streamlit + Plotly** | v2.0 Pro Edition
