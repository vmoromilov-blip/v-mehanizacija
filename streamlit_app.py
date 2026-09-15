import streamlit as st
import pandas as pd
import os
from datetime import datetime

# UVOZIMO NAŠE FIOKE ZA ISPRAVNOST I RASPORED
from ispravnost import prikazi_ispravnost
from raspored import prikazi_raspored

st.set_page_config(page_title="Operativni Izveštaji", layout="wide")
st.title("🚜 Operativni izveštaji mehanizacije")

st.sidebar.header("Meni sa modulima")
# PROMENJENO IME U MENIJU: UMESTO "DNEVNI RASPORED" SADA PIŠE "RASPORED"
modul = st.sidebar.radio("Izaberi modul:", ["Početna", "SPISAK MAŠINA", "SPISAK RADNIKA", "ZAMENA", "PRIMALAC MAIL-A", "NOSIOCI", "ISPRAVNOST", "RASPORED"])

fajl_baze = 'plan.xlsm'

if modul == "Početna":
    st.write("### Dobrodošli u operativni sistem mehanizacije!")
    st.write("Izaberite modul sa leve strane kako biste videli podatke.")
    
elif modul == "SPISAK MAŠINA":
    st.write("## 📋 Spisak mehanizacije")
    if os.path.exists(fajl_baze):
        df_masine = pd.read_excel(fajl_baze, sheet_name='SPISAK MAŠINA')
        st.dataframe(df_masine, use_container_width=True)
    else:
        st.error("Fajl nije pronađen.")

elif modul == "SPISAK RADNIKA":
    st.write("## 👥 Spisak zaposlenih radnika")
    if os.path.exists(fajl_baze):
        df_radnici = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
        prikaz_df = df_radnici.drop(columns=['EMAIL ADRESA', 'TIP', 'Unnamed: 3'], errors='ignore')
        st.dataframe(prikaz_df, use_container_width=True)
    else:
        st.error("Fajl nije pronađen.")

elif modul == "ZAMENA":
    st.write("## 🔄 Spisak i evidencija zamena")
    if os.path.exists(fajl_baze):
        df_zamena = pd.read_excel(fajl_baze, sheet_name='ZAMENA')
        df_zamena = df_zamena.rename(columns={'START DATUM': 'DATUM POČETKA', 'END DATUM': 'DATUM ZAVRŠETKA'})
        if 'DATUM POČETKA' in df_zamena.columns:
            df_zamena['DATUM POČETKA'] = pd.to_datetime(df_zamena['DATUM POČETKA']).dt.date
        if 'DATUM ZAVRŠETKA' in df_zamena.columns:
            df_zamena['DATUM ZAVRŠETKA'] = pd.to_datetime(df_zamena['DATUM ZAVRŠETKA']).dt.date
        st.dataframe(df_zamena, use_container_width=True)

elif modul == "PRIMALAC MAIL-A":
    st.write("## 📧 Ljudi kojima se šalje izveštaj")
    if os.path.exists(fajl_baze):
        df_radnici = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
        if 'EMAIL ADRESA' in df_radnici.columns:
            df_mail = df_radnici[df_radnici['EMAIL ADRESA'].notna() & (df_radnici['EMAIL ADRESA'] != '')]
            kolone_za_prikaz = [col for col in ['EMAIL ADRESA', 'TIP'] if col in df_mail.columns]
            st.dataframe(df_mail[kolone_za_prikaz], use_container_width=True)

elif modul == "NOSIOCI":
    st.write("## 🔑 Zaduženja mehanizacije - Nosioci")
    if os.path.exists(fajl_baze):
        df_nosioci = pd.read_excel(fajl_baze, sheet_name='NOSIOCI').drop(columns=['TIP'], errors='ignore')
        df_nosioci = df_nosioci.rename(columns={'START DATUM': 'DATUM POČETKA'})
        if 'DATUM POČETKA' in df_nosioci.columns:
            df_nosioci['DATUM POČETKA'] = pd.to_datetime(df_nosioci['DATUM POČETKA']).dt.date
        st.dataframe(df_nosioci, use_container_width=True)

elif modul == "ISPRAVNOST":
    prikazi_ispravnost(fajl_baze)

# KADA SE KLIKNE NA RASPORED, OTVARA SE FIOKA ZA RASPORED
elif modul == "RASPORED":
    prikazi_raspored(fajl_baze)
