import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
from fpdf import FPDF
import io

# --- 1. CONFIGURATION (DOIT ÊTRE LA TOUTE PREMIÈRE LIGNE) ---
st.set_page_config(page_title="SAD MINISTERE DU COMMERCE | Guinée", layout="wide", initial_sidebar_state="expanded")

# --- 2. STYLE CSS SÉCURISÉ (FIXE LE DÉCALAGE ET LA COULEUR) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-image: linear-gradient(180deg, rgba(206,17,38,0.15), rgba(252,209,22,0.15), rgba(0,148,96,0.15)) !important;
        border-right: 5px solid #fcd116 !important;
    }
    .stMetric {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-bottom: 5px solid #009460;
    }
    h1 { color: #009460 !important; font-weight: 800; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GÉNÉRATEUR DE DONNÉES (DYNAMISME TOTAL) ---
def load_full_data():
    regions = ['Conakry', 'Kindia', 'Boké', 'Mamou', 'Labé', 'Faranah', 'Kankan', 'Nzérékoré']
    produits = {
        'Riz Local': 8500, 'Riz Importé': 12500, 'Sucre': 14000, 
        'Huile Végétale': 250000, 'Farine': 7500, 'Ciment': 950000
    }
    coords = {
        'Conakry': [9.53, -13.67], 'Kindia': [10.04, -12.86], 'Boké': [10.93, -14.29],
        'Mamou': [10.37, -12.09], 'Labé': [11.31, -12.28], 'Faranah': [10.04, -10.74],
        'Kankan': [10.38, -9.30], 'Nzérékoré': [7.75, -8.81]
    }
    data = []
    for reg in regions:
        for prod, base in produits.items():
            dist = 1.3 if reg in ['Kankan', 'Nzérékoré'] else 1.0
            price = base * dist * np.random.uniform(0.9, 1.1)
            data.append({
                'Date': datetime.now(),
                'Région': reg,
                'Produit': prod,
                'Prix_GNF': price,
                'Stock_T': np.random.randint(50, 5000),
                'Besoin_Hebdo': np.random.randint(100, 1500),
                'lat': coords[reg][0],
                'lon': coords[reg][1]
            })
    return pd.DataFrame(data)

# --- 4. BARRE LATÉRALE ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Flag_of_Guinea.svg/320px-Flag_of_Guinea.svg.png", width=120)
    st.title("Pilotage Stratégique")
    st.markdown("---")
    
    mode = st.radio("Mode de données", ["Démonstration (IA)", "Charger CSV Ministère"])
    
    if mode == "Charger CSV Ministère":
        up = st.file_uploader("Fichier .csv", type="csv")
        df_raw = pd.read_csv(up) if up else load_full_data()
    else:
        df_raw = load_full_data()

    st.markdown("### Filtres")
    sel_prod = st.selectbox("Produit ciblé", df_raw['Produit'].unique(), key="prod_main")
    sel_regions = st.multiselect("Zones", df_raw['Région'].unique(), default=df_raw['Région'].unique())

# --- 5. LOGIQUE DE FILTRAGE ---
df_f = df_raw[(df_raw['Produit'] == sel_prod) & (df_raw['Région'].isin(sel_regions))]

# --- 6. ENTÊTE ---
st.title("🇬🇳 Cockpit de Pilotage Stratégique 360°")
st.markdown(f"**Ministère du Commerce - Secrétariat Général** | Analyse du : {datetime.now().strftime('%d/%m/%Y')}")

# --- 7. ONGLETS ---
t1, t2, t3, t4 = st.tabs(["📊 Diagnostic Prix", "📦 Stock & Logistique", "🌍 Veille Internationale", "📝 Rapport PDF"])

with t1:
    c1, c2, c3 = st.columns(3)
    avg_p = df_f['Prix_GNF'].mean()
    c1.metric(f"Prix Moyen {sel_prod}", f"{avg_p:,.0f} GNF", "+2.5%")
    c2.metric("Stock Total", f"{df_f['Stock_T'].sum():,.0f} T")
    c3.metric("Zones en Alerte", "2 Zones", delta_color="inverse")

    st.markdown("### 🗺️ Carte Dynamique des Tensions")
    # Ajout d'une colonne de taille pour la carte
    df_f['size_map'] = df_f['Prix_GNF'] / 100
    st.map(df_f, latitude='lat', longitude='lon', size='size_map', color='#ce1126')
    
    fig_p = px.bar(df_f, x='Région', y='Prix_GNF', color='Prix_GNF', color_continuous_scale="RdYlGn_r", title="Comparatif des Prix par Région")
    st.plotly_chart(fig_p, use_container_width=True)

with t2:
    st.subheader("📦 État des Réserves et Capacité Logistique")
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        fig_stock = px.pie(df_f, values='Stock_T', names='Région', hole=0.4, title="Répartition des Stocks")
        st.plotly_chart(fig_stock, use_container_width=True)
    
    with col_s2:
        df_f['Couverture'] = df_f['Stock_T'] / (df_f['Besoin_Hebdo'] / 7)
        fig_cov = px.bar(df_f, x='Région', y='Couverture', title="Autonomie en jours (par Région)", color='Couverture')
        st.plotly_chart(fig_cov, use_container_width=True)

with t3:
    st.subheader("🌍 Sentinelle : Surveillance des Marchés Mondiaux")
    col_v1, col_v2 = st.columns([2, 1])
    
    with col_v1:
        # Simulation indice mondial
        mondial = pd.DataFrame({'Mois': range(1,7), 'Indice': [100, 105, 120, 150, 140, 160]})
        fig_v = px.area(mondial, x='Mois', y='Indice', title="Évolution du Fret et Matières Premières (Index)")
        st.plotly_chart(fig_v, use_container_width=True)
    
    with col_v2:
        st.error("🚨 ALERTE IMPORTATION")
        st.write(f"Le segment **{sel_prod}** subit une pression logistique majeure. Prévision de hausse : **+12%** sous 15 jours.")
        st.info("Action recommandée : Libérer les stocks régulateurs.")

with t4:
    st.subheader("📝 Note de Synthèse & Export")
    comm = st.text_area("Observations du Cabinet", f"Analyse du {sel_prod} : Les stocks sont suffisants à Conakry mais critiques en Haute-Guinée...")
    
    if st.button("📄 Générer le Rapport PDF"):
        st.balloons()
        st.success("Rapport PDF prêt (Simulation).")
        # Logique PDF simplifiée pour éviter les erreurs de buffer
        st.download_button("Télécharger la Note", data=comm, file_name="note_synthese.txt")

st.markdown("---")
st.caption("💻 SAD-COMMERCE v4.0 | Conception : Almamy Kalla Bangoura")