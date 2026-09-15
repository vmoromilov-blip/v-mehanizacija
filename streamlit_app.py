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
modul = st.sidebar.radio("Izaberi modul:", ["Početna", "SPISAK MAŠINA", "SPISAK RADNIKA", "ZAMENA", "PRIMALAC MAIL-A", "NOSIOCI", "ISPRAVNOST", "RASPORED"])

fajl_baze = 'plan.xlsm'

if modul == "Početna":
    st.write("### Dobrodošli u operativni sistem mehanizacije!")
    st.write("Izaberite modul sa leve strane kako biste videli podatke.")
    
elif modul == "SPISAK MAŠINA":
    st.write("## 📋 Spisak mehanizacije")
    if os.path.exists(fajl_baze):
        df_masine = pd.read_excel(fajl_baze, sheet_name='SPISAK MAŠINA')
        
        # DUGMIĆI IZNAD TABELE MAŠINA - POPRAVLJENO SA (2)
        col1, col2 = st.columns(2)
        with col1:
            with st.popover("➕ Dodaj mašinu"):
                novi_tip = st.text_input("Tip mašine (npr. BAGER):")
                novi_gb = st.text_input("Garažni broj (npr. GB4760):")
                if st.button("Sačuvaj mašinu"):
                    st.success("Mašina ubačena!")
                    st.rerun()
        with col2:
            if st.button("🗑️ Obriši selektovane mašine"):
                st.success("Izabrani redovi uklonjeni!")
                st.rerun()

        st.write("")
        st.data_editor(df_masine, use_container_width=True, num_rows="dynamic", key="editor_masine")
    else:
        st.error("Fajl nije pronađen.")

elif modul == "SPISAK RADNIKA":
    st.write("## 👥 Spisak zaposlenih radnika")
    if os.path.exists(fajl_baze):
        df_radnici = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
        prikaz_df = df_radnici.drop(columns=['EMAIL ADRESA', 'TIP', 'Unnamed: 3'], errors='ignore')

        # DUGMIĆI IZNAD TABELE RADNIKA - POPRAVLJENO SA (2)
        col1, col2 = st.columns(2)
        with col1:
            with st.popover("➕ Dodaj radnika"):
                novo_ime = st.text_input("Ime i prezime radnika:")
                if st.button("Sačuvaj radnika"):
                    st.success("Radnik ubačen!")
                    st.rerun()
        with col2:
            if st.button("🗑️ Obriši selektovane radnike"):
                st.success("Izabrani radnici uklonjeni!")
                st.rerun()

        st.write("")
        st.data_editor(prikaz_df, use_container_width=True, num_rows="dynamic", key="editor_radnici")
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
            
        col1, col2 = st.columns(2)
        with col1:
            with st.popover("➕ Dodaj zamenu"):
                osnovno = st.text_input("Šta/Ko se menja:")
                zamenski = st.text_input("Šta/Ko je zamena:")
                if st.button("Sačuvaj zamenu"):
                    st.success("Zamena uneta!")
                    st.rerun()
        with col2:
            if st.button("🗑️ Ukloni selektovane zamene"):
                st.success("Zamene obrisane!")
                st.rerun()

        st.write("")
        st.data_editor(df_zamena, use_container_width=True, num_rows="dynamic", key="editor_zamena")

elif modul == "PRIMALAC MAIL-A":
    st.write("## 📧 Ljudi kojima se šalje izveštaj")
    if os.path.exists(fajl_baze):
        df_radnici = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
        if 'EMAIL ADRESA' in df_radnici.columns:
            df_mail = df_radnici[df_radnici['EMAIL ADRESA'].notna() & (df_radnici['EMAIL ADRESA'] != '')]
            kolone_za_prikaz = [col for col in ['EMAIL ADRESA', 'TIP'] if col in df_mail.columns]
            
            col1, col2 = st.columns(2)
            with col1:
                with st.popover("➕ Dodaj email"):
                    novi_email = st.text_input("Email adresa:")
                    tip_slanja = st.selectbox("Izaberi tip slanja:", ["TO", "CC"])
                    if st.button("Sačuvaj email"):
                        st.success("Email dodat!")
                        st.rerun()
            with col2:
                if st.button("🗑️ Ukloni selektovane mejlove"):
                    st.success("Email uklonjen!")
                    st.rerun()

            st.write("")
            st.data_editor(df_mail[kolone_za_prikaz], use_container_width=True, num_rows="dynamic", key="editor_mail")

elif modul == "NOSIOCI":
    st.write("## 🔑 Zaduženja mehanizacije - Nosioci")
    if os.path.exists(fajl_baze):
        df_nosioci = pd.read_excel(fajl_baze, sheet_name='NOSIOCI').drop(columns=['TIP'], errors='ignore')
        df_nosioci = df_nosioci.rename(columns={'START DATUM': 'DATUM POČETKA'})
        if 'DATUM POČETKA' in df_nosioci.columns:
            df_nosioci['DATUM POČETKA'] = pd.to_datetime(df_nosioci['DATUM POČETKA']).dt.date
            
        col1, col2 = st.columns(2)
        with col1:
            with st.popover("➕ Dodaj nosioca"):
                radnik_unos = st.text_input("Prezime i ime radnika:")
                gb_unos = st.text_input("Garažni broj mašine:")
                if st.button("Sačuvaj zaduženje"):
                    st.success("Zaduženje uneto!")
                    st.rerun()
        with col2:
            if st.button("🗑️ Raskini selektovana zaduženja"):
                st.success("Zaduženja obrisana!")
                st.rerun()

        st.write("")
        st.data_editor(df_nosioci, use_container_width=True, num_rows="dynamic", key="editor_nosioci")

elif modul == "ISPRAVNOST":
    prikazi_ispravnost(fajl_baze)

elif modul == "RASPORED":
    prikazi_raspored(fajl_baze)
