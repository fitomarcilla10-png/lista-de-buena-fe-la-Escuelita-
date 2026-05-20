import streamlit as st
import pandas as pd
import json
from datetime import date, datetime
import base64
import io

# ============ CONFIGURACIÓN DE PÁGINA ============
st.set_page_config(
    page_title="Club Basket - Gestión de Jugadores",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============ ESTILOS CSS ============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;500;600;700&display=swap');
    
    .stApp { background-color: #11111b; color: #e4e4e7; }
    header[data-testid="stHeader"] { background-color: #1e1e2e; border-bottom: 1px solid #2a2a3e; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #1e1e2e; padding: 6px; border-radius: 12px; border: 1px solid #2a2a3e; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; color: #9ca3af; border-radius: 8px; padding: 10px 20px; font-weight: 600; font-family: 'DM Sans', sans-serif; }
    .stTabs [aria-selected="true"] { background-color: #f97316 !important; color: white !important; }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 2rem; }
    
    div[data-testid="stForm"] { background-color: #1e1e2e; border: 1px solid #2a2a3e; border-radius: 12px; padding: 1.5rem; }
    .stTextInput > div > div > input, .stNumberInput > div > div > input, .stDateInput > div > div > input,
    .stSelectbox > div > div, .stTextArea > div > div > textarea {
        background-color: #181825 !important; border-color: #3a3a4e !important; color: #e4e4e7 !important; border-radius: 8px !important;
    }
    .stTextInput > label, .stNumberInput > label, .stDateInput > label, .stSelectbox > label, .stTextArea > label {
        color: #9ca3af !important; font-size: 0.75rem !important; text-transform: uppercase !important; letter-spacing: 0.05em !important; font-weight: 600 !important;
    }
    
    .section-card { background-color: #1e1e2e; border: 1px solid #2a2a3e; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; }
    .section-title { font-family: 'Bebas Neue', sans-serif; font-size: 1.4rem; color: #f4f4f5; letter-spacing: 0.05em; margin-bottom: 1rem;
        padding-bottom: 0.75rem; border-bottom: 1px solid #2a2a3e; display: flex; align-items: center; gap: 0.75rem; }
    .section-icon { width: 32px; height: 32px; border-radius: 8px; background: rgba(249,115,22,0.1); display: flex; align-items: center; justify-content: center; font-size: 1rem; }
    
    .brand-header { background: linear-gradient(135deg, #1e1e2e 0%, #11111b 100%); border: 1px solid #2a2a3e; border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: 1.5rem;
        display: flex; align-items: center; gap: 1rem; }
    .brand-logo { width: 48px; height: 48px; border-radius: 12px; background: linear-gradient(135deg, #f97316, #c2410c); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 8px 24px rgba(249,115,22,0.2); }
    .brand-text h1 { font-family: 'Bebas Neue', sans-serif; font-size: 2rem; color: white; margin: 0; letter-spacing: 0.1em; line-height: 1; }
    .brand-text p { font-size: 0.65rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.2em; margin: 0; }
    
    .minor-alert { background: rgba(249,115,22,0.1); border: 1px solid rgba(249,115,22,0.3); border-radius: 8px; padding: 0.75rem 1rem; color: #fb923c; font-size: 0.8rem; font-weight: 600; margin-bottom: 1rem; }
    .age-badge { background: rgba(249,115,22,0.1); border: 1px solid rgba(249,115,22,0.3); border-radius: 8px; padding: 0.5rem 1rem; color: #fb923c; font-weight: 700; font-size: 0.9rem; text-align: center; }
    .category-badge { background: rgba(249,115,22,0.15); border: 1px solid rgba(249,115,22,0.4); border-radius: 8px; padding: 0.5rem 1rem; color: #f97316; font-weight: 800; font-size: 1rem; text-align: center; font-family: 'Bebas Neue', sans-serif; letter-spacing: 0.1em; }
    
    .doc-status { display: inline-flex; align-items: center; gap: 4px; }
    .doc-ok { color: #4ade80; }
    .doc-missing { color: #6b7280; }
    
    div[data-testid="stDataFrame"] { border: 1px solid #2a2a3e; border-radius: 12px; overflow: hidden; }
    .stButton > button { border-radius: 8px !important; font-weight: 600 !important; font-family: 'DM Sans', sans-serif !important; }
    
    .stDownloadButton > button { background: #16a34a !important; color: white !important; border: none !important; }
    .stDownloadButton > button:hover { background: #15803d !important; }
</style>
""", unsafe_allow_html=True)

# ============ UTILIDADES ============
def calculate_age(birth_date):
    if not birth_date:
        return None
    today = date.today()
    if isinstance(birth_date, str):
        birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def calculate_category(birth_date):
    if not birth_date:
        return ""
    if isinstance(birth_date, str):
        birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
    current_year = date.today().year
    age = current_year - birth_date.year
    if age <= 13: return "U13"
    elif age <= 15: return "U15"
    elif age <= 17: return "U17"
    elif age <= 19: return "U19"
    elif age <= 21: return "U21"
    else: return "Mayores"

def get_players():
    if "players" not in st.session_state:
        st.session_state.players = get_mock_players()
    return st.session_state.players

def save_players(players):
    st.session_state.players = players

def get_mock_players():
    return [
        {
            "id": "1", "fullName": "Gonzalez Matías", "dni": "45678901", "birthDate": "2010-03-15", "gender": "Masculino",
            "address": "Av. San Martín 1234, CABA", "phone": "1155667788", "email": "matias.gonzalez@email.com",
            "height": 165, "weight": 58, "shirtSize": "M", "shortSize": "M", "jacketSize": "L", "shirtName": "MATI",
            "bloodType": "A+", "healthInsurance": "OSDE", "affiliateNumber": "123456", "allergies": "Ninguna",
            "medicalConditions": "Ninguna", "medications": "Ninguno",
            "emergencyName": "Laura Gonzalez", "emergencyRelation": "Madre", "emergencyPhone": "1144332211",
            "tutorName": "Laura Gonzalez", "tutorDni": "28765432", "tutorRelation": "Madre", "tutorPhone": "1144332211", "tutorEmail": "laura.g@email.com",
            "files": {"photo": True, "dniFront": True, "dniBack": False, "dniTutor": True, "medCert": True}
        },
        {
            "id": "2", "fullName": "Rodriguez Facundo", "dni": "38901234", "birthDate": "1998-07-22", "gender": "Masculino",
            "address": "Calle Belgrano 567, Córdoba", "phone": "3514455667", "email": "facu.rodriguez@email.com",
            "height": 188, "weight": 82, "shirtSize": "XL", "shortSize": "L", "jacketSize": "XL", "shirtName": "FACU",
            "bloodType": "O-", "healthInsurance": "Swiss Medical", "affiliateNumber": "789012", "allergies": "Penicilina",
            "medicalConditions": "Ninguna", "medications": "Ninguno",
            "emergencyName": "Carlos Rodriguez", "emergencyRelation": "Padre", "emergencyPhone": "3519988776",
            "tutorName": "", "tutorDni": "", "tutorRelation": "", "tutorPhone": "", "tutorEmail": "",
            "files": {"photo": True, "dniFront": True, "dniBack": True, "dniTutor": False, "medCert": False}
        }
    ]

def export_csv(players):
    headers = ['Apellido y Nombre','DNI','Fecha Nacimiento','Edad','Género','Categoría','Dirección','Teléfono','Email',
               'Altura (cm)','Peso (kg)','Talle Camiseta','Talle Pantalón','Talle Buzo','Nombre Camiseta',
               'Grupo Sanguíneo','Obra Social','Nro Afiliado','Alergias','Condiciones Médicas','Medicamentos',
               'Contacto Emergencia Nombre','Contacto Emergencia Parentesco','Contacto Emergencia Teléfono',
               'Tutor Nombre','Tutor DNI','Tutor Parentesco','Tutor Teléfono','Tutor Email']
    rows = []
    for p in players:
        rows.append([
            p.get("fullName",""), p.get("dni",""), p.get("birthDate",""), calculate_age(p.get("birthDate")),
            p.get("gender",""), calculate_category(p.get("birthDate")), p.get("address",""), p.get("phone",""), p.get("email",""),
            p.get("height",""), p.get("weight",""), p.get("shirtSize",""), p.get("shortSize",""), p.get("jacketSize",""), p.get("shirtName",""),
            p.get("bloodType",""), p.get("healthInsurance",""), p.get("affiliateNumber",""), p.get("allergies",""),
            p.get("medicalConditions",""), p.get("medications",""),
            p.get("emergencyName",""), p.get("emergencyRelation",""), p.get("emergencyPhone",""),
            p.get("tutorName",""), p.get("tutorDni",""), p.get("tutorRelation",""), p.get("tutorPhone",""), p.get("tutorEmail","")
        ])
    df = pd.DataFrame(rows, columns=headers)
    csv = df.to_csv(index=False, sep=';', encoding='utf-8-sig')
    return csv

# ============ HEADER ============
st.markdown("""
<div class="brand-header">
    <div class="brand-logo">🏀</div>
    <div class="brand-text">
        <h1>CLUB BASKET</h1>
        <p>Sistema de Gestión de Jugadores</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ============ TABS ============
tab_form, tab_db = st.tabs(["📋 Ficha de Inscripción", "🗄️ Base de Datos General"])

# ============ TAB 1: FORMULARIO ============
with tab_form:
    
    # Inicializar estado de edición
    if "editing_id" not in st.session_state:
        st.session_state.editing_id = None
    
    editing_player = None
    if st.session_state.editing_id:
        players = get_players()
        editing_player = next((p for p in players if p["id"] == st.session_state.editing_id), None)
    
    with st.form("inscription_form", clear_on_submit=True):
        
        # ---- SECCIÓN 1: Datos Personales ----
        st.markdown("""<div class="section-card"><div class="section-title"><div class="section-icon">👤</div> DATOS PERSONALES Y DE CONTACTO</div></div>""", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            full_name = st.text_input("Apellido(s) y Nombre(s) *", value=editing_player["fullName"] if editing_player else "")
            gender = st.selectbox("Género / Rama *", ["", "Masculino", "Femenino"], index=["", "Masculino", "Femenino"].index(editing_player["gender"]) if editing_player and editing_player.get("gender") in ["Masculino", "Femenino"] else 0)
            address = st.text_input("Dirección de Residencia", value=editing_player["address"] if editing_player else "")
        with col2:
            dni = st.text_input("DNI / Pasaporte *", value=editing_player["dni"] if editing_player else "")
            phone = st.text_input("Teléfono Celular *", value=editing_player["phone"] if editing_player else "")
            email = st.text_input("Correo Electrónico", value=editing_player["email"] if editing_player else "")
        with col3:
            default_date = datetime.strptime(editing_player["birthDate"], "%Y-%m-%d").date() if editing_player and editing_player.get("birthDate") else date(2005, 1, 1)
            birth_date = st.date_input("Fecha de Nacimiento *", value=default_date, min_value=date(1970, 1, 1), max_value=date.today())
            
            age = calculate_age(birth_date)
            category = calculate_category(birth_date)
            
            st.markdown(f'<div class="age-badge">Edad: {age} años</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="category-badge">{category}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ---- SECCIÓN 2: Datos Deportivos ----
        st.markdown("""<div class="section-card"><div class="section-title"><div class="section-icon">🏀</div> DATOS DEPORTIVOS Y FICHA TÉCNICA</div></div>""", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            height = st.number_input("Altura (cm)", min_value=100, max_value=230, value=editing_player.get("height", 170) if editing_player else 170)
        with col2:
            weight = st.number_input("Peso (kg)", min_value=30, max_value=150, value=editing_player.get("weight", 70) if editing_player else 70)
        with col3:
            st.markdown(f'<br><div class="category-badge">Categoría: {category}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ---- SECCIÓN 3: Indumentaria ----
        st.markdown("""<div class="section-card"><div class="section-title"><div class="section-icon">👕</div> LOGÍSTICA E INDUMENTARIA</div></div>""", unsafe_allow_html=True)
        
        sizes = ["", "S", "M", "L", "XL", "XXL", "XXXL"]
        sizes_no_xxxl = ["", "S", "M", "L", "XL", "XXL"]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            shirt_size = st.selectbox("Talle Camiseta", sizes, index=sizes.index(editing_player.get("shirtSize","")) if editing_player and editing_player.get("shirtSize","") in sizes else 0)
        with col2:
            short_size = st.selectbox("Talle Pantalón/Short", sizes_no_xxxl, index=sizes_no_xxxl.index(editing_player.get("shortSize","")) if editing_player and editing_player.get("shortSize","") in sizes_no_xxxl else 0)
        with col3:
            jacket_size = st.selectbox("Talle Buzo/Campera", sizes_no_xxxl, index=sizes_no_xxxl.index(editing_player.get("jacketSize","")) if editing_player and editing_player.get("jacketSize","") in sizes_no_xxxl else 0)
        with col4:
            shirt_name = st.text_input("Nombre en Camiseta", value=editing_player.get("shirtName","") if editing_player else "")
        
        st.markdown("---")
        
        # ---- SECCIÓN 4: Control Médico ----
        st.markdown("""<div class="section-card"><div class="section-title"><div class="section-icon">❤️</div> CONTROL MÉDICO Y SALUD</div></div>""", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            blood_types = ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            blood_type = st.selectbox("Grupo Sanguíneo y Factor", blood_types, index=blood_types.index(editing_player.get("bloodType","")) if editing_player and editing_player.get("bloodType","") in blood_types else 0)
            allergies = st.text_area("Alergias Conocidas", value=editing_player.get("allergies","") if editing_player else "", placeholder="Medicamentos, alimentos, picaduras...")
        with col2:
            health_insurance = st.text_input("Obra Social / Prepaga", value=editing_player.get("healthInsurance","") if editing_player else "")
            medical_conditions = st.text_area("Condiciones Médicas / Crónicas", value=editing_player.get("medicalConditions","") if editing_player else "", placeholder="Asma, diabetes, etc.")
        with col3:
            affiliate_number = st.text_input("Número de Afiliado", value=editing_player.get("affiliateNumber","") if editing_player else "")
            medications = st.text_area("Medicamentos de Uso Diario", value=editing_player.get("medications","") if editing_player else "")
        
        st.markdown("**Contacto de Emergencia**")
        col1, col2, col3 = st.columns(3)
        with col1:
            emergency_name = st.text_input("Nombre Completo (Emergencia) *", value=editing_player.get("emergencyName","") if editing_player else "")
        with col2:
            emergency_relation = st.text_input("Parentesco", value=editing_player.get("emergencyRelation","") if editing_player else "")
        with col3:
            emergency_phone = st.text_input("Teléfono (Emergencia) *", value=editing_player.get("emergencyPhone","") if editing_player else "")
        
        st.markdown("---")
        
        # ---- SECCIÓN 5: Tutor ----
        is_minor = age is not None and age < 18
        
        if is_minor:
            st.markdown("""<div class="section-card"><div class="section-title"><div class="section-icon">🛡️</div> DATOS DE MENORES (TUTOR/RESPONSABLE)</div></div>""", unsafe_allow_html=True)
            st.markdown('<div class="minor-alert">⚠️ El jugador es menor de edad. Estos campos son OBLIGATORIOS.</div>', unsafe_allow_html=True)
        else:
            st.markdown("""<div class="section-card"><div class="section-title"><div class="section-icon">🛡️</div> DATOS DE MENORES (TUTOR/RESPONSABLE) — Opcional</div></div>""", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            tutor_name = st.text_input("Nombre y Apellido del Tutor" + (" *" if is_minor else ""), value=editing_player.get("tutorName","") if editing_player else "")
            relations = ["", "Madre", "Padre", "Tutor Legal"]
            tutor_relation = st.selectbox("Parentesco (Tutor)", relations, index=relations.index(editing_player.get("tutorRelation","")) if editing_player and editing_player.get("tutorRelation","") in relations else 0)
        with col2:
            tutor_dni = st.text_input("DNI del Tutor" + (" *" if is_minor else ""), value=editing_player.get("tutorDni","") if editing_player else "")
            tutor_phone = st.text_input("Teléfono del Tutor" + (" *" if is_minor else ""), value=editing_player.get("tutorPhone","") if editing_player else "")
        with col3:
            tutor_email = st.text_input("Correo Electrónico del Tutor", value=editing_player.get("tutorEmail","") if editing_player else "")
        
        st.markdown("---")
        
        # ---- SECCIÓN 6: Documentos ----
        st.markdown("""<div class="section-card"><div class="section-title"><div class="section-icon">📁</div> DOCUMENTACIÓN Y ARCHIVOS ADJUNTOS</div></div>""", unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            photo_file = st.file_uploader("Foto de Perfil", type=["jpg","jpeg","png"], key="photo")
        with col2:
            dni_front_file = st.file_uploader("DNI Frente", type=["jpg","jpeg","png","pdf"], key="dni_front")
        with col3:
            dni_back_file = st.file_uploader("DNI Dorso", type=["jpg","jpeg","png","pdf"], key="dni_back")
        with col4:
            dni_tutor_file = st.file_uploader("DNI del Tutor", type=["jpg","jpeg","png","pdf"], key="dni_tutor")
        with col5:
            med_cert_file = st.file_uploader("Certificado Médico", type=["jpg","jpeg","png","pdf"], key="med_cert")
        
        st.markdown("---")
        
        # ---- BOTONES ----
        col_btn1, col_btn2, col_btn3 = st.columns([4, 1, 1])
        with col_btn2:
            if editing_player:
                cancel = st.form_submit_button("Cancelar", type="secondary")
        with col_btn3:
            submitted = st.form_submit_button("💾 Registrar Jugador" if not editing_player else "💾 Actualizar", type="primary")
        
        if submitted:
            # Validaciones
            if not full_name or not dni or not gender:
                st.error("Complete los campos obligatorios: Nombre, DNI y Género.")
            elif is_minor and (not tutor_name or not tutor_dni or not tutor_phone):
                st.error("Para menores de edad, los datos del tutor (Nombre, DNI y Teléfono) son obligatorios.")
            else:
                new_player = {
                    "id": editing_player["id"] if editing_player else str(datetime.now().timestamp()),
                    "fullName": full_name, "dni": dni, "birthDate": birth_date.strftime("%Y-%m-%d"), "gender": gender,
                    "address": address, "phone": phone, "email": email,
                    "height": height, "weight": weight,
                    "shirtSize": shirt_size, "shortSize": short_size, "jacketSize": jacket_size, "shirtName": shirt_name,
                    "bloodType": blood_type, "healthInsurance": health_insurance, "affiliateNumber": affiliate_number,
                    "allergies": allergies, "medicalConditions": medical_conditions, "medications": medications,
                    "emergencyName": emergency_name, "emergencyRelation": emergency_relation, "emergencyPhone": emergency_phone,
                    "tutorName": tutor_name, "tutorDni": tutor_dni, "tutorRelation": tutor_relation, "tutorPhone": tutor_phone, "tutorEmail": tutor_email,
                    "files": {
                        "photo": bool(photo_file) or (editing_player and editing_player.get("files",{}).get("photo", False)),
                        "dniFront": bool(dni_front_file) or (editing_player and editing_player.get("files",{}).get("dniFront", False)),
                        "dniBack": bool(dni_back_file) or (editing_player and editing_player.get("files",{}).get("dniBack", False)),
                        "dniTutor": bool(dni_tutor_file) or (editing_player and editing_player.get("files",{}).get("dniTutor", False)),
                        "medCert": bool(med_cert_file) or (editing_player and editing_player.get("files",{}).get("medCert", False)),
                    }
                }
                
                players = get_players()
                if editing_player:
                    players = [new_player if p["id"] == editing_player["id"] else p for p in players]
                    st.session_state.editing_id = None
                else:
                    players.append(new_player)
                save_players(players)
                st.success(f"{'Jugador actualizado' if editing_player else 'Jugador registrado'}: {full_name}")
                st.rerun()

# ============ TAB 2: BASE DE DATOS ============
with tab_db:
    players = get_players()
    
    # Toolbar
    col_search, col_cat, col_gen, col_export = st.columns([3, 2, 2, 2])
    with col_search:
        search = st.text_input("🔍 Buscar por nombre o DNI", placeholder="Buscar...", label_visibility="collapsed")
    with col_cat:
        filter_cat = st.selectbox("Categoría", ["Todas", "U13", "U15", "U17", "U19", "U21", "Mayores"], label_visibility="collapsed")
    with col_gen:
        filter_gen = st.selectbox("Rama", ["Todas", "Masculino", "Femenino"], label_visibility="collapsed")
    with col_export:
        csv_data = export_csv(players)
        st.download_button("📥 Exportar a Excel (CSV)", data=csv_data, file_name="jugadores_club_basquet.csv", mime="text/csv")
    
    # Filtrar
    filtered = players.copy()
    if search:
        filtered = [p for p in filtered if search.lower() in p.get("fullName","").lower() or search in p.get("dni","")]
    if filter_cat != "Todas":
        filtered = [p for p in filtered if calculate_category(p.get("birthDate")) == filter_cat]
    if filter_gen != "Todas":
        filtered = [p for p in filtered if p.get("gender") == filter_gen]
    
    st.caption(f"{len(filtered)} de {len(players)} jugadores")
    
    # Tabla
    if filtered:
        for i, player in enumerate(filtered):
            cat = calculate_category(player.get("birthDate"))
            files = player.get("files", {})
            docs_icons = ""
            for key in ["photo", "dniFront", "dniBack", "dniTutor", "medCert"]:
                if files.get(key):
                    docs_icons += "🟢"
                else:
                    docs_icons += "⚫"
            
            talles = f"C:{player.get('shirtSize','—')} | P:{player.get('shortSize','—')}"
            
            with st.container():
                col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([3, 2, 1.5, 1.5, 2, 2.5, 2, 1.5])
                with col1:
                    st.markdown(f"**{player.get('fullName','')}**")
                with col2:
                    st.code(player.get('dni',''), language=None)
                with col3:
                    st.markdown(f"`{cat}`")
                with col4:
                    st.caption(player.get('gender',''))
                with col5:
                    st.caption(talles)
                with col6:
                    st.caption(f"{player.get('emergencyName','')}\n{player.get('emergencyPhone','')}")
                with col7:
                    st.markdown(docs_icons)
                with col8:
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✏️", key=f"edit_{player['id']}"):
                            st.session_state.editing_id = player["id"]
                            st.rerun()
                    with c2:
                        if st.button("🗑️", key=f"del_{player['id']}"):
                            players_updated = [p for p in get_players() if p["id"] != player["id"]]
                            save_players(players_updated)
                            st.rerun()
                st.divider()
    else:
        st.info("No se encontraron jugadores.")
