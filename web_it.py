import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- KONFIGURIMI ---
PASSWORD_STAF = "grezda2025" 
PASSWORD_ADMIN = "adminit2025" # Ky eshte kodi qe do perdoresh vetem TI

st.set_page_config(page_title="IT Portal - Isa Grezda", page_icon="🏥", layout="wide")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    st.title("🏥 Portali IT - Spitali Isa Grezda")
    pwd = st.text_input("Shkruani kodin e stafit:", type="password")
    if st.button("Hyr"):
        if pwd == PASSWORD_STAF or pwd == PASSWORD_ADMIN:
            st.session_state["password_correct"] = True
            st.session_state["is_admin"] = (pwd == PASSWORD_ADMIN) # Identifikon nese je TI
            st.rerun()
        else:
            st.error("❌ Kodi i gabuar!")
    return False

if check_password():
    DATA_FILE = 'log_asistenca_it.csv'
    
    # Menaxhimi i Tab-eve bazuar ne ate kush eshte kyçur
    if st.session_state.get("is_admin", False):
        tabs = st.tabs(["📝 Raporto Defekt", "📊 Dashboard", "📋 Tabela e Punëve"])
    else:
        tabs = st.tabs(["📝 Raporto Defekt"]) # Infermieret shohin vetem kete

    # --- TABI 1: RAPORTO (E shohin te gjithe) ---
    with tabs[0]:
        st.header("Regjistro një problem të ri")
        with st.form("form_kerkesa", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                emri = st.text_input("Emri i personit")
                reparti = st.selectbox("Reparti", ["Emergjenca", "Radiologjia", "Laboratori", "Pediatria", "Kirurgjia", "Administrata"])
            with col2:
                tel = st.text_input("Nr. i Kontaktit")
                prioriteti = st.radio("Prioriteti:", ["E Rregullt", "URGJENTE"], horizontal=True)
            
            problemi = st.text_area("Përshkrimi i problemit")
            if st.form_submit_button("DËRGO KËRKESËN"):
                në_kohë = datetime.now().strftime("%Y-%m-%d %H:%M")
                df_re = pd.DataFrame([[në_kohë, emri, reparti, tel, problemi, prioriteti, "E Re"]], 
                                     columns=["Data/Ora", "Emri", "Reparti", "Telefoni", "Problemi", "Prioriteti", "Statusi"])
                df_re.to_csv(DATA_FILE, mode='a', header=not os.path.exists(DATA_FILE), index=False)
                st.success("✅ Kërkesa u dërgua me sukses!")

    # --- Tabet e tjera: Shfaqen VETEM nese je Admin ---
    if st.session_state.get("is_admin", False):
        with tabs[1]:
            st.header("Analiza IT")
            if os.path.exists(DATA_FILE):
                df = pd.read_csv(DATA_FILE)
                st.metric("Gjithsej Kërkesa", len(df))
                st.bar_chart(df['Reparti'].value_counts())
        
        with tabs[2]:
            st.header("Lista e kërkesave")
            if os.path.exists(DATA_FILE):
                df_view = pd.read_csv(DATA_FILE)
                st.dataframe(df_view.sort_index(ascending=False), use_container_width=True)

    if st.sidebar.button("Dil (Logout)"):
        st.session_state["password_correct"] = False
        st.rerun()