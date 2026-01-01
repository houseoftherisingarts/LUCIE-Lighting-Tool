import streamlit as st
import ezdxf
from ezdxf import bbox
import math
import csv
import os

# --- 1. CONFIG & BRANDING ---
APP_NAME = "L.U.C.I.E."
APP_SUBTITLE_EN = "Universal Calculation & Lighting Intelligence Engine"
APP_SUBTITLE_FR = "Logiciel Universel de Calcul & Intelligence Éclairage"

st.set_page_config(page_title=APP_NAME, page_icon="✨", layout="wide")

# --- 2. THE "APPLE STORE" CSS INJECTION ---
APPLE_CSS = """
<style>
    /* IMPORT APPLE-SYSTEM FONT */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #FFFFFF !important; /* FORCE WHITE TEXT */
    }

    /* MAIN BACKGROUND */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #2c2c2e 0%, #000000 100%);
    }

    /* CARD STYLING */
    div[data-testid="stFileUploader"], div[data-testid="stMetricValue"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 30px;
        padding: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    div[data-testid="stFileUploader"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 122, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* BUTTONS */
    div.stButton > button {
        background: linear-gradient(135deg, #007AFF 0%, #0055B3 100%);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 15px 40px;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 122, 255, 0.4);
        width: 100%;
    }

    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(0, 122, 255, 0.6);
    }
    
    div.stButton > button::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        height: 40px;
        background: inherit;
        filter: blur(15px);
        opacity: 0.4;
        transform: scaleY(-1);
        pointer-events: none;
    }

    /* HEADERS */
    h1 {
        font-weight: 700;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #FFFFFF 0%, #A1A1AA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(255,255,255,0.1);
    }

    /* FOOTER SIGNATURE */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        color: rgba(255, 255, 255, 0.3);
        font-size: 12px;
        padding: 20px;
        pointer-events: none;
        font-family: "Inter", sans-serif;
        letter-spacing: 1px;
    }
</style>
"""
st.markdown(APPLE_CSS, unsafe_allow_html=True)

# --- 3. LANGUAGE DICTIONARY ---
LANG = {
    "EN": {
        "title": f"✨ {APP_NAME}",
        "subtitle": f"{APP_SUBTITLE_EN}",
        "tab_calc": "⚡ Core Engine",
        "tab_help": "🧠 Knowledge Base",
        "sidebar_settings": "Parameters",
        "target_fc": "Target Footcandles (fc)",
        "upload_dxf": "1. Environment (.dxf)",
        "upload_ies": "2. Photometrics (.ies)",
        "select_fixture": "Active Fixture Protocol",
        "btn_generate": "Initialize Calculation",
        "reading_files": "Processing geometry...",
        "success": "Calculation Complete",
        "room_dim": "Dimensions",
        "fixture_data": "Fixture Data",
        "lumens": "Output",
        "grid": "Grid Matrix",
        "efficiency": "Density",
        "download": "📥 Download Data Packet",
        "warning_agi": "⚠️ AGI32 Protocol: Rename Label to:",
        "error_dxf": "Error: Unreadable Geometry. Save CAD as DXF 2013.",
        "error_zero": "Void Detected: Area is 0.",
        "dxf_instruction": "Required: DXF (2013 Version)",
        "tutorial_title": "Operator Manual",
        "step1": "Phase 1: Prep",
        "step1_desc": "Convert CAD to .dxf. Gather .ies files.",
        "step2": "Phase 2: Ingest",
        "step2_desc": "Drag & Drop files into the glass cards.",
        "step3": "Phase 3: Calibrate",
        "step3_desc": "Set Target FC. Select fixture.",
        "step4": "Phase 4: Export",
        "step4_desc": "Download data. Import to AGI32.",
    },
    "FR": {
        "title": f"✨ {APP_NAME}",
        "subtitle": f"{APP_SUBTITLE_FR}",
        "tab_calc": "⚡ Moteur Central",
        "tab_help": "🧠 Base de Savoir",
        "sidebar_settings": "Paramètres",
        "target_fc": "Cible Éclairement (fc)",
        "upload_dxf": "1. Environnement (.dxf)",
        "upload_ies": "2. Photométrie (.ies)",
        "select_fixture": "Luminaire Actif",
        "btn_generate": "Initialiser le Calcul",
        "reading_files": "Traitement de la géométrie...",
        "success": "Calcul Terminé",
        "room_dim": "Dimensions",
        "fixture_data": "Données Luminaire",
        "lumens": "Flux (lm)",
        "grid": "Matrice",
        "efficiency": "Densité",
        "download": "📥 Télécharger le Paquet",
        "warning_agi": "⚠️ Protocole AGI32 : Renommer l'étiquette en :",
        "error_dxf": "Erreur : Géométrie Illisible. Sauvegarder en DXF 2013.",
        "error_zero": "Vide Détecté : Surface = 0.",
        "dxf_instruction": "Requis : DXF (Version 2013)",
        "tutorial_title": "Manuel Opérateur",
        "step1": "Phase 1 : Préparation",
        "step1_desc": "Convertir CAD en .dxf. Obtenir fichiers .ies.",
        "step2": "Phase 2 : Ingestion",
        "step2_desc": "Glisser-déposer les fichiers dans les cartes.",
        "step3": "Phase 3 : Calibration",
        "step3_desc": "Définir Cible FC. Sélectionner le luminaire.",
        "step4": "Phase 4 : Export",
        "step4_desc": "Télécharger. Importer dans AGI32.",
    }
}

# --- 4. LANGUAGE TOGGLE (DEFAULT FRENCH) ---
# Note: index=0 means first option is default. We put Français first now.
lang_option = st.sidebar.radio("Langue / Language", ["Français", "English"], horizontal=True)
L_CODE = "FR" if lang_option == "Français" else "EN"
TXT = LANG[L_CODE]

# --- 5. MAIN HEADER ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title(TXT["title"])
    st.caption(TXT["subtitle"])

# --- 6. HELPER FUNCTIONS ---
def get_lumens_from_ies(ies_content):
    try:
        text = ies_content.decode("utf-8", errors="ignore")
        lines = text.split('\n')
        for line in lines:
            if "IUMENS" in line.upper() or "LUMENS" in line.upper():
                 parts = line.split()
                 for p in parts:
                     if p.isdigit() and int(p) > 100:
                         return int(p)
        import re
        numbers = re.findall(r'\b\d+\b', text)
        for n in numbers:
            if 300 < int(n) < 50000: 
                return int(n)
        return 4000 
    except:
        return 4000 

def process_project(dxf_file, ies_file, target_fc):
    # 1. READ CAD
    try:
        with open("temp.dxf", "wb") as f:
            f.write(dxf_file.getbuffer())   
        doc = ezdxf.readfile("temp.dxf")
        msp = doc.modelspace()
        extent = bbox.extents(msp)
        
        if not extent.has_data:
             return None, None, None, None, None, None, TXT["error_dxf"]

        width = extent.extmax.x - extent.extmin.x
        length = extent.extmax.y - extent.extmin.y
        start_x = extent.extmin.x
        start_y = extent.extmin.y
        
    except Exception as e:
        return None, None, None, None, None, None, f"{TXT['error_dxf']} ({str(e)})"

    # 2. READ IES
    real_lumens = get_lumens_from_ies(ies_file.getvalue())
    
    # 3. CALCULATE OPTIMIZATION
    area = width * length
    if area == 0: return None, None, None, None, None, None, TXT["error_zero"]

    needed_lumens = (target_fc * area) / (0.85 * 0.9)
    total_lights = math.ceil(needed_lumens / real_lumens)
    
    aspect_ratio = width / length
    rows = math.sqrt(total_lights / aspect_ratio)
    cols = total_lights / rows
    rows, cols = max(1, round(rows)), max(1, round(cols))
    
    density = area / (rows*cols)

    # 4. GENERATE OUTPUT
    output_lines = ["Label,X,Y,Z,Orient,Tilt"]
    spacing_x = width / cols
    spacing_y = length / rows
    
    label_name = os.path.splitext(ies_file.name)[0]
    label_name = "".join(x for x in label_name if x.isalnum())
    
    for r in range(int(rows)):
        for c in range(int(cols)):
            x = start_x + (c * spacing_x) + (spacing_x / 2)
            y = start_y + (r * spacing_y) + (spacing_y / 2)
            z = 9.5 
            output_lines.append(f"{label_name},{x:.2f},{y:.2f},{z:.2f},0,0")
            
    csv_content = "\n".join(output_lines)
    
    return f"{width:.1f}x{length:.1f}", real_lumens, csv_content, label_name, f"{int(cols)}x{int(rows)}", f"{density:.1f} sqft/unit", None

# --- 7. TABS LAYOUT ---
tab1, tab2 = st.tabs([TXT["tab_calc"], TXT["tab_help"]])

# === TAB 1: CALCULATOR ===
with tab1:
    # Sidebar
    st.sidebar.header(TXT["sidebar_settings"])
    target_fc = st.sidebar.number_input(TXT["target_fc"], value=50, step=5)
    st.sidebar.markdown("---")
    
    # --- GLASS CARDS LAYOUT ---
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_dxf = st.file_uploader(TXT["upload_dxf"], type=["dxf"])
        
    with col2:
        uploaded_ies_list = st.file_uploader(TXT["upload_ies"], type=["ies"], accept_multiple_files=True)

    # Fixture Selection
    selected_ies = None
    if uploaded_ies_list:
        ies_names = [f.name for f in uploaded_ies_list]
        choice_name = st.selectbox(TXT["select_fixture"], ies_names)
        for f in uploaded_ies_list:
            if f.name == choice_name:
                selected_ies = f

    # ACTION BUTTON
    st.markdown("<br>", unsafe_allow_html=True) 
    
    if uploaded_dxf and selected_ies:
        if st.button(TXT["btn_generate"], type="primary"):
            with st.spinner(TXT["reading_files"]):
                room_size, lumens, csv_data, label, grid_size, density, error = process_project(uploaded_dxf, selected_ies, target_fc)
                
                if error:
                    st.error(error)
                else:
                    st.success(TXT["success"])
                    
                    # GLASS METRIC CARDS
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric(TXT["room_dim"], room_size)
                    m2.metric(TXT["lumens"], lumens)
                    m3.metric(TXT["grid"], grid_size)
                    m4.metric(TXT["efficiency"], density)
                    
                    st.download_button(
                        label=TXT["download"],
                        data=csv_data,
                        file_name=f"{label}_LUCIE_Data.txt",
                        mime="text/csv"
                    )
                    st.info(f"{TXT['warning_agi']} **{label}**")
    elif uploaded_dxf or uploaded_ies_list:
        st.caption("En attente des données complètes..." if L_CODE == "FR" else "Waiting for complete data set...")

# === TAB 2: TUTORIAL ===
with tab2:
    st.header(TXT["tutorial_title"])
    st.markdown(f"""
    ### {TXT['step1']}
    {TXT['step1_desc']}
    
    ### {TXT['step2']}
    {TXT['step2_desc']}
    
    ### {TXT['step3']}
    {TXT['step3_desc']}
    
    ### {TXT['step4']}
    {TXT['step4_desc']}
    """)

# --- 8. SUBTLE SIGNATURE ---
st.markdown("""
    <div class="footer">
        Outil conceptualisé par Le Salon des Inconnus
    </div>
""", unsafe_allow_html=True)
