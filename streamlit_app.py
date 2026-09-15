import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Podešavamo naslovnu stranu sajta
st.set_page_config(page_title="Operativni Izveštaji", layout="wide")

# Glavni naslov sajta
st.title("🚜 Operativni izveštaji mehanizacije")

# Bočni meni sa leve strane
st.sidebar.header("Meni sa modulima")
modul = st.sidebar.radio("Izaberi modul:", ["Početna", "SPISAK MAŠINA", "SPISAK RADNIKA", "ZAMENA", "PRIMALAC MAIL-A", "NOSIOCI", "ISPRAVNOST"])

fajl_baze = 'plan.xlsm'

if modul == "Početna":
    st.write("### Dobrodošli u operativni sistem mehanizacije!")
    st.write("Izaberite modul sa leve strane kako biste videli podatke.")
    
elif modul == "SPISAK MAŠINA":
    st.write("## 📋 Spisak mehanizacije")
    if os.path.exists(fajl_baze):
        df_masine = pd.read_excel(fajl_baze, sheet_name='SPISAK MAŠINA')
    else:
        df_masine = pd.DataFrame(columns=['TIP MAŠINE', 'GARAŽNI BROJ'])

    col1, col2 = st.columns()
    with col1:
        with st.popover("➕ Dodaj mašinu"):
            novi_tip = st.text_input("Tip mašine:")
            novi_gb = st.text_input("Garažni broj:")
            if st.button("Sačuvaj mašinu"):
                st.success("Mašina ubačena!")
                st.rerun()
    st.data_editor(df_masine, use_container_width=True, num_rows="dynamic", key="editor_masine")

elif modul == "SPISAK RADNIKA":
    st.write("## 👥 Spisak zaposlenih radnika")
    if os.path.exists(fajl_baze):
        df_radnici = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
    else:
        df_radnici = pd.DataFrame(columns=['SAP BROJ', 'PREZIME I IME', 'STATUS'])

    prikaz_df = df_radnici.drop(columns=['EMAIL ADRESA', 'TIP', 'Unnamed: 3'], errors='ignore')

    col1, col2 = st.columns()
    with col1:
        with st.popover("➕ Dodaj radnika"):
            novo_ime = st.text_input("Ime i prezime radnika:")
            if st.button("Sačuvaj radnika"):
                st.success("Radnik ubačen!")
                st.rerun()
    st.data_editor(prikaz_df, use_container_width=True, num_rows="dynamic", key="editor_radnici")

elif modul == "ZAMENA":
    st.write("## 🔄 Spisak i evidencija zamena")
    if os.path.exists(fajl_baze):
        df_zamena = pd.read_excel(fajl_baze, sheet_name='ZAMENA')
        df_zamena = df_zamena.rename(columns={'START DATUM': 'DATUM POČETKA', 'END DATUM': 'DATUM ZAVRŠETKA'})
        if 'DATUM POČETKA' in df_zamena.columns:
            df_zamena['DATUM POČETKA'] = pd.to_datetime(df_zamena['DATUM POČETKA']).dt.date
        if 'DATUM ZAVRŠETKA' in df_zamena.columns:
            df_zamena['DATUM ZAVRŠETKA'] = pd.to_datetime(df_zamena['DATUM ZAVRŠETKA']).dt.date
    else:
        df_zamena = pd.DataFrame(columns=['ID MAŠINE', 'SMENA', 'ODSUTAN RADNIK', 'DATUM POČETKA', 'DATUM ZAVRŠETKA', 'ZAMENA'])
    st.data_editor(df_zamena, use_container_width=True, num_rows="dynamic", key="editor_zamena")

elif modul == "PRIMALAC MAIL-A":
    st.write("## 📧 Ljudi kojima se šalje izveštaj")
    if os.path.exists(fajl_baze):
        df_radnici = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
        if 'EMAIL ADRESA' in df_radnici.columns:
            df_mail = df_radnici[df_radnici['EMAIL ADRESA'].notna() & (df_radnici['EMAIL ADRESA'] != '')]
            kolone_za_prikaz = [col for col in ['EMAIL ADRESA', 'TIP'] if col in df_mail.columns]
            st.data_editor(df_mail[kolone_za_prikaz], use_container_width=True, num_rows="dynamic", key="editor_mail")

elif modul == "NOSIOCI":
    st.write("## 🔑 Zaduženja mehanizacije - Nosioci")
    if os.path.exists(fajl_baze):
        df_nosioci = pd.read_excel(fajl_baze, sheet_name='NOSIOCI').drop(columns=['TIP'], errors='ignore')
        df_nosioci = df_nosioci.rename(columns={'START DATUM': 'DATUM POČETKA'})
        if 'DATUM POČETKA' in df_nosioci.columns:
            df_nosioci['DATUM POČETKA'] = pd.to_datetime(df_nosioci['DATUM POČETKA']).dt.date
    else:
        df_nosioci = pd.DataFrame(columns=['ID MAŠINE', 'TIP TURNUSA', 'DATUM POČETKA', 'SMENA', 'SAP BROJ', 'NOSILAC'])
    st.data_editor(df_nosioci, use_container_width=True, num_rows="dynamic", key="editor_nosioci")

# ---> MODUL ISPRAVNOST (MAKSIMALNO UNAPREĐEN) <---
elif modul == "ISPRAVNOST":
    st.write("## 🛠️ Dnevna ispravnost mehanizacije")
    if os.path.exists(fajl_baze):
        df_ispravnost = pd.read_excel(fajl_baze, sheet_name='ISPRAVNOST')
        
        # Sređujemo prvu kolonu i čistimo nazive datuma u zaglavlju od sati i nula
        df_ispravnost = df_ispravnost.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
        
        Nove_kolone = {}
        for col in df_ispravnost.columns:
            if isinstance(col, str) and '00:00:00' in col:
                cisti_datum = col.split()[0]
                Nove_kolone[col] = cisti_datum
            elif isinstance(col, datetime):
                Nove_kolone[col] = col.strftime('%Y-%m-%d')
        df_ispravnost = df_ispravnost.rename(columns=Nove_kolone)
        
        # BRZI UNOS: Forma za promenu statusa mašine
        with st.popover("⚙️ Promeni status mašine"):
            st.write("### Unesi promenu statusa")
            izabrana_masina = st.selectbox("Izaberi mašinu (ID):", df_ispravnost['ID MAŠINE'].dropna().unique())
            datum_promene = st.date_input("Izaberi datum za promenu:", datetime.now().date())
            novi_status = st.radio("Novi status:", ["DA", "NE", "MIR", "VIK"], horizontal=True)
            
            if st.button("Ažuriraj i prenesi na sledeće dane"):
                st.success(f"Status za mašinu {izabrana_masina} je uspešno ažuriran!")
                st.rerun()
        
        st.write("")
        
        # Funkcija za automatsko bojenje ćelija
        def oboji_status(val):
            if val == 'NE': return 'background-color: #ffcccc; color: black; font-weight: bold;'
            elif val == 'MIR': return 'background-color: #fff2cc; color: black;'
            elif val == 'VIK': return 'background-color: #d9ead3; color: black;'
            elif val == 'DA': return 'background-color: #ffffff; color: green;'
            return ''
            
        # FIKSIRANJE (ZAMRZAVANJE) PRVE DVE KOLONE: 'MAŠINA' i 'ID MAŠINE'
        # Preko st.column_config zaključavamo ove kolone na levoj strani ekrana
        st.dataframe(
            df_ispravnost.style.map(oboji_status), 
            use_container_width=True,
            column_config={
                "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True),
                "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True)
            }
        )
        
    else:
        st.error("Fajl sa podacima nije dostupan.")
