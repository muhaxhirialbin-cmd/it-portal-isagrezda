import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- KONFIGURIMI I SIGURISË ---
# Mund ta ndryshosh këtë fjalëkalim si të dëshirosh
PASSWORD_STAF = "grezda2025" 

def check_password():
    """Kthehet True nëse përdoruesi jep fjalëkalimin e saktë."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Shfaq forma e login-it
    st.title("🏥 Portali IT - Spitali Isa Grezda")
    pwd = st.text_input("Ju lutem shkruani kodin e stafit për të vazhduar:", type="password")
    if st.button("Hyr"):
        if pwd == PASSWORD_STAF:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ Kodi i gabuar!")
    return False

# Kontrollojmë fjalëkalimin para se të shfaqim faqen
if check_password():

    st.set_page_config(page_title="IT Portal - Isa Grezda", page_icon="🏥", layout="wide")

    DATA_FILE = 'log_asistenca_it.csv'

    # Header dhe Stili
    st.markdown("""
        <style>
        .stApp { max-width: 1200px; margin: 0 auto; }
        .stButton>button { background-color: #004a99; color: white; }
        </style>
        """, unsafe_allow_html=True)

    st.title("🏥 Sistemi i Menaxhimit IT")
    st.subheader("Mirësevini, staf i Spitalit 'Isa Grezda'")
    st.divider()

    # Funksioni për të lexuar të dhënat
    def lexo_te_dhenat():
        if os.path.exists(DATA_FILE):
            return pd.read_csv(DATA_FILE)
        return pd.DataFrame(columns=["Data/Ora", "Emri", "Reparti", "Telefoni", "Problemi", "Prioriteti", "Statusi"])

    # Tabet e Faqes
    tab1, tab2, tab3 = st.tabs(["📝 Raporto Defekt", "📊 Dashboard", "📋 Tabela e Punëve"])

    with tab1:
        st.header("Regjistro një problem të ri")
        with st.form("form_kerkesa", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                emri = st.text_input("Emri i personit")
                reparti = st.selectbox("Reparti", ["Emergjenca", "Radiologjia", "Laboratori", "Pediatria", "Kirurgjia", "Administrata", "Gjinekologjia", "Ortopedia"])
            with col2:
                tel = st.text_input("Nr. i Kontaktit")
                prioriteti = st.radio("Prioriteti:", ["E Rregullt", "URGJENTE"], horizontal=True)
            
            problemi = st.text_area("Përshkrimi i problemit")
            submit = st.form_submit_button("DËRGO KËRKESËN")
            
            if submit:
                në_kohë = datetime.now().strftime("%Y-%m-%d %H:%M")
                re_data = [[në_kohë, emri, reparti, tel, problemi, prioriteti, "E Re"]]
                df_re = pd.DataFrame(re_data, columns=["Data/Ora", "Emri", "Reparti", "Telefoni", "Problemi", "Prioriteti", "Statusi"])
                
                if not os.path.isfile(DATA_FILE):
                    df_re.to_csv(DATA_FILE, index=False)
                else:
                    df_re.to_csv(DATA_FILE, mode='a', header=False, index=False)
                st.success("✅ Kërkesa u regjistrua!")

    with tab2:
        df = lexo_te_dhenat()
        if not df.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("Gjithsej Kërkesa", len(df))
            m2.metric("Urgjente 🚨", len(df[df['Prioriteti'] == 'URGJENTE']))
            m3.metric("Të Rregullta ✅", len(df[df['Prioriteti'] == 'E Rregullt']))
            st.bar_chart(df['Reparti'].value_counts())
        else:
            st.info("Nuk ka të dhëna për grafikë.")

    with tab3:
        st.header("Lista e kërkesave")
        df_view = lexo_te_dhenat()
        if not df_view.empty:
            st.dataframe(df_view.sort_index(ascending=False), use_container_width=True)
        else:
            st.write("Lista është bosh.")

    # Butoni për Logout në fund
    if st.sidebar.button("Dil (Logout)"):
        st.session_state["password_correct"] = False
        st.rerun()