import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- KONFIGURIMI I SIGURISË ---
PASSWORD_STAF = "grezda2025" 
PASSWORD_ADMIN = "adminit2025"  # Ndryshoje këtë në diçka më të sigurt

# Konfigurimi i faqes
st.set_page_config(page_title="IT Portal - Isa Grezda", page_icon="🏥", layout="wide")

# Funksioni për kontrollin e fjalëkalimit
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if st.session_state["password_correct"]:
        return True

    # Ndërfaqja e hyrjes (Login)
    st.markdown("<h1 style='text-align: center;'>🏥 Portali IT - Isa Grezda</h1>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd = st.text_input("Shkruani kodin për të vazhduar:", type="password")
        if st.button("Hyr në Sistem"):
            if pwd == PASSWORD_STAF or pwd == PASSWORD_ADMIN:
                st.session_state["password_correct"] = True
                st.session_state["is_admin"] = (pwd == PASSWORD_ADMIN)
                st.rerun()
            else:
                st.error("❌ Kodi i gabuar! Provoni përsëri.")
    return False

# Nëse fjalëkalimi është i saktë, shfaqet përmbajtja
if check_password():
    DATA_FILE = 'log_asistenca_it.csv'

    # Header-i i faqes
    st.title("🏥 Sistemi i Menaxhimit IT")
    if st.session_state.get("is_admin", False):
        st.subheader("Mirësevini, Administrator IT")
    else:
        st.subheader("Mirësevini, Stafi i Spitalit 'Isa Grezda'")
    st.divider()

    # Funksioni për leximin e të dhënave
    def lexo_te_dhenat():
        if os.path.exists(DATA_FILE):
            return pd.read_csv(DATA_FILE)
        return pd.DataFrame(columns=["Data/Ora", "Emri", "Reparti", "Telefoni", "Problemi", "Prioriteti", "Statusi"])

    # Menaxhimi i Tab-eve (Infermieri sheh vetëm formën, Admini sheh gjithçka)
    if st.session_state.get("is_admin", False):
        tabs = st.tabs(["➕ Raporto Defekt", "📊 Dashboard", "📋 Tabela e Punëve"])
    else:
        tabs = st.tabs(["➕ Raporto Defekt"])

    # --- TABI 1: RAPORTIMI (Për të gjithë) ---
    with tabs[0]:
        st.header("Raporto një problem të ri")
        with st.form("form_kerkesa", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                emri = st.text_input("Emri i personit që raporton")
                reparti = st.selectbox("Reparti", [
                    "Emergjenca", "Radiologjia", "Laboratori", 
                    "Pediatria", "Kirurgjia", "Gjinekologjia", 
                    "Ortopedia", "Administrata", "Dializa", "Kardiologjia"
                ])
            with col2:
                tel = st.text_input("Nr. i Kontaktit / Lokali")
                prioriteti = st.radio("Prioriteti:", ["E Rregullt", "URGJENTE"], horizontal=True)
            
            problemi = st.text_area("Përshkrimi i problemit")
            
            if st.form_submit_button("DËRGO KËRKESËN"):
                if emri and problemi:
                    në_kohë = datetime.now().strftime("%Y-%m-%d %H:%M")
                    re_data = [[në_kohë, emri, reparti, tel, problemi, prioriteti, "E Re"]]
                    df_re = pd.DataFrame(re_data, columns=["Data/Ora", "Emri", "Reparti", "Telefoni", "Problemi", "Prioriteti", "Statusi"])
                    
                    # Ruajtja lokale në CSV
                    df_re.to_csv(DATA_FILE, mode='a', header=not os.path.exists(DATA_FILE), index=False)
                    st.success(f"✅ Faleminderit {emri}, kërkesa juaj u regjistrua me sukses!")
                else:
                    st.warning("Ju lutem plotësoni Emrin dhe Përshkrimin e problemit.")

    # --- TABET E ADMINIT (Vetëm për IT) ---
    if st.session_state.get("is_admin", False):
        df = lexo_te_dhenat()
        
        with tabs[1]:
            st.header("Statistikat e Ndërhyrjeve")
            if not df.empty:
                m1, m2, m3 = st.columns(3)
                m1.metric("Gjithsej Kërkesa", len(df))
                m2.metric("Urgjente 🚨", len(df[df['Prioriteti'] == 'URGJENTE']))
                m3.metric("Reparti me më shumë punë", df['Reparti'].mode()[0] if not df['Reparti'].empty else "N/A")
                
                st.write("#### Shpërndarja sipas Reparteve")
                st.bar_chart(df['Reparti'].value_counts())
            else:
                st.info("Nuk ka të dhëna për të shfaqur grafikë.")

        with tabs[2]:
            st.header("Lista e të gjitha punëve")
            if not df.empty:
                # Mundësia për kërkim (Search)
                kerko = st.text_input("🔍 Kërko (Reparti, Emri ose Problemi)")
                if kerko:
                    df = df[df.apply(lambda row: kerko.lower() in row.astype(str).str.lower().values, axis=1)]
                
                st.dataframe(df.sort_index(ascending=False), use_container_width=True)
                
                # Opcion për shkarkim në Excel/CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Shkarko Tabelën (CSV)", csv, "raporti_it.csv", "text/csv")
            else:
                st.write("Tabela është bosh aktualisht.")

    # Butoni i daljes në sidebar
    with st.sidebar:
        st.write(f"Përdoruesi: {'Admin' if st.session_state.get('is_admin') else 'Staf'}")
        if st.button("Dil (Logout)"):
            st.session_state["password_correct"] = False
            st.rerun()