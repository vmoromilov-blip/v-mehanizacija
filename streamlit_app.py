import streamlit as st
import pandas as pd
import os
from datetime import datetime

# UVOZIMO NAŠE MODULE IZ POSEBNIH FIOKA
from GARAŽNA_BAZA import prikazi_garazu
from POSADA_BAZA import prikazi_posadu
from ispravnost import prikazi_ispravnost
from raspored import prikazi_raspored

# Podešavamo sajt da fabrički uvek koristi maksimalnu širinu ekrana
st.set_page_config(page_title="Operativni Izveštaji", layout="wide")

st.sidebar.header("MENI SA MODULIMA")
modul = st.sidebar.radio("IZABERI MODUL:", ["POČETNA", "GARAŽA", "SPISAK VOZAČA", "ZAMENA", "NOSIOCI", "ISPRAVNOST", "RASPORED"])

fajl_baze = 'plan.xlsm'

if modul == "POČETNA":
    st.write("### Dobrodošli u operativni sistem mehanizacije!")
    st.write("Izaberite modul sa leve strane kako biste videli podatke.")
    
elif modul == "GARAŽA":
    prikazi_garazu(fajl_baze)

elif modul == "SPISAK VOZAČA":
    prikazi_posadu(fajl_baze)

elif modul == "ZAMENA":
    st.write("## 🔄 Spisak i evidencija zamena")
    if os.path.exists(fajl_baze):
        df_zamena = pd.read_excel(fajl_baze, sheet_name='ZAMENA')
        st.data_editor(df_zamena, use_container_width=True, num_rows="dynamic", key="editor_zamena")

elif modul == "NOSIOCI":
    st.write("## 🔑 Zaduženja mehanizacije - Nosioci")
    if os.path.exists(fajl_baze):
        df_nosioci = pd.read_excel(fajl_baze, sheet_name='NOSIOCI')
        st.data_editor(df_nosioci, use_container_width=True, num_rows="dynamic", key="editor_nosioci")

elif modul == "ISPRAVNOST":
    prikazi_ispravnost(fajl_baze)

elif modul == "RASPORED":
    prikazi_raspored(fajl_baze)
