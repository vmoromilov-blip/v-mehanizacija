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

def ucitaj_ili_napravi_bazu(sheet_name, default_cols):
    fajl_csv = f"{sheet_name.lower().replace(' ', '_')}.csv"
    if os.path.exists(fajl_csv):
        return pd.read_csv(fajl_csv)
    elif os.path.exists(fajl_baze):
        try:
            df = pd.read_excel(fajl_baze, sheet_name=sheet_name)
            df.to_csv(fajl_csv, index=False)
            return df
        except:
            return pd.DataFrame(columns=default_cols)
    return pd.DataFrame(columns=default_cols)

def sacuvaj_bazu(df, sheet_name):
    fajl_csv = f"{sheet_name.lower().replace(' ', '_')}.csv"
    df.to_csv(fajl_csv, index=False)

if modul == "Početna":
    st.write("### Dobrodošli u operativni sistem mehanizacije!")
    st.write("Izaberite modul sa leve strane kako biste videli podatke.")
    
elif modul == "SPISAK MAŠINA":
    st.write("## 📋 Spisak mehanizacije")
    df_masine = ucitaj_ili_napravi_bazu('SPISAK MAŠINA', ['TIP MAŠINE', 'GARAŽNI BROJ'])
    col1, col2 = st.columns(2)
    with col1:
        with st.popover("➕ Dodaj mašinu"):
            novi_tip = st.text_input("Tip mašine (npr. BAGER):")
            novi_gb = st.text_input("Garažni broj (npr. GB4760):")
            if st.button("Sačuvaj mašinu"):
                if novi_tip and novi_gb:
                    novi_red = pd.DataFrame([{'TIP MAŠINE': novi_tip.upper(), 'GARAŽNI BROJ': novi_gb.upper()}])
                    df_masine = pd.concat([df_masine, novi_red], ignore_index=False)
                    sacuvaj_bazu(df_masine, 'SPISAK MAŠINA')
                    st.success("Mašina upisana!")
                    st.rerun()
    with col2:
        st.info("Štiklirajte kućicu levo i pritisnite ikonicu kante u tabeli za brisanje.")
    st.write("")
    edited_df = st.data_editor(df_masine, use_container_width=True, num_rows="dynamic", key="editor_masine")
    if edited_df is not None and not edited_df.equals(df_masine):
        sacuvaj_bazu(edited_df, 'SPISAK MAŠINA')
        st.rerun()

elif modul == "SPISAK RADNIKA":
    st.write("## 👥 Spisak zaposlenih radnika")
    df_radnici = ucitaj_ili_napravi_bazu('SPISAK RADNIKA', ['SAP BROJ', 'PREZIME I IME', 'STATUS'])
    if 'EMAIL ADRESA' in df_radnici.columns:
        df_radnici = df_radnici.drop(columns=['EMAIL ADRESA', 'TIP', 'Unnamed: 3'], errors='ignore')
    col1, col2 = st.columns(2)
    with col1:
        with st.popover("➕ Dodaj radnika"):
            novo_ime = st.text_input("Prezime i ime radnika:")
            novi_sap = st.text_input("SAP Broj:")
            if st.button("Sačuvaj radnika"):
                if novo_ime:
                    novi_red = pd.DataFrame([{'SAP BROJ': novi_sap, 'PREZIME I IME': novo_ime.upper(), 'STATUS': 'AKTIVAN'}])
                    df_radnici = pd.concat([df_radnici, novi_red], ignore_index=False)
                    sacuvaj_bazu(df_radnici, 'SPISAK RADNIKA')
                    st.success("Radnik upisan!")
                    st.rerun()
    st.write("")
    edited_df = st.data_editor(df_radnici, use_container_width=True, num_rows="dynamic", key="editor_radnici")
    if edited_df is not None and not edited_df.equals(df_radnici):
        sacuvaj_bazu(edited_df, 'SPISAK RADNIKA')
        st.rerun()

elif modul == "ZAMENA":
    st.write("## 🔄 Spisak i evidencija zamena")
    df_zamena = ucitaj_ili_napravi_bazu('ZAMENA', ['ID MAŠINE', 'SMENA', 'ODSUTAN RADNIK', 'DATUM POČETKA', 'DATUM ZAVRŠETKA', 'ZAMENA'])
    df_zamena = df_zamena.rename(columns={'START DATUM': 'DATUM POČETKA', 'END DATUM': 'DATUM ZAVRŠETKA'})
    
    # Čistimo sate i nule iz datuma u koloni
    for col in ['DATUM POČETKA', 'DATUM ZAVRŠETKA']:
        if col in df_zamena.columns:
            df_zamena[col] = pd.to_datetime(df_zamena[col]).dt.date

    col1, col2 = st.columns(2)
    with col1:
        with st.popover("➕ Dodaj zamenu"):
            st.write("### Unesi podatke za novu zamenu")
            z_id = st.text_input("Garažni broj mašine:")
            z_smena = st.text_input("Smena:")
            z_odsutan = st.text_input("Odsutan radnik:")
            z_pocetak = st.date_input("Datum početka:")
            z_zavrsetak = st.date_input("Datum završetka:")
            z_zamena = st.text_input("Ko je zamena:")
            
            if st.button("Sačuvaj zamenu"):
                novi_red = pd.DataFrame([{
                    'ID MAŠINE': z_id.upper(), 'SMENA': z_smena.upper(),
                    'ODSUTAN RADNIK': z_odsutan.upper(), 'DATUM POČETKA': str(z_pocetak),
                    'DATUM ZAVRŠETKA': str(z_zavrsetak), 'ZAMENA': z_zamena.upper()
                }])
                df_zamena = pd.concat([df_zamena, novi_red], ignore_index=False)
                sacuvaj_bazu(df_zamena, 'ZAMENA')
                st.success("Zamena uspešno upisana!")
                st.rerun()
    with col2:
        if st.button("🗑️ Obriši selektovane zamene"):
            st.info("Štiklirajte redove levo u tabeli i upotrebite ikonicu kante za uklanjanje starih zamena.")
                
    st.write("")
    edited_df = st.data_editor(df_zamena, use_container_width=True, num_rows="dynamic", key="editor_zamena")
    if edited_df is not None and not edited_df.equals(df_zamena):
        sacuvaj_bazu(edited_df, 'ZAMENA')
        st.rerun()

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
    df_nosioci = ucitaj_ili_napravi_bazu('NOSIOCI', ['ID MAŠINE', 'TIP TURNUSA', 'DATUM POČETKA', 'SMENA', 'SAP BROJ', 'NOSILAC'])
    df_nosioci = df_nosioci.rename(columns={'START DATUM': 'DATUM POČETKA'})
    col1, col2 = st.columns(2)
    with col1:
        with st.popover("➕ Dodaj nosioca"):
            novi_id = st.text_input("Garažni broj mašine (ID MAŠINE):")
            novi_turnus = st.text_input("Tip turnusa:")
            nova_smena = st.text_input("Smena:")
            novi_sap_br = st.text_input("SAP Broj:")
            novi_nosilac_ime = st.text_input("Prezime i ime radnika:")
            if st.button("Sačuvaj zaduženje"):
                novi_red = pd.DataFrame([{
                    'ID MAŠINE': novi_id.upper(), 'TIP TURNUSA': novi_turnus,
                    'DATUM POČETKA': datetime.now().strftime('%Y-%m-%d'), 'SMENA': nova_smena.upper(),
                    'SAP BROJ': novi_sap_br, 'NOSILAC': novi_nosilac_ime.upper()
                }])
                df_nosioci = pd.concat([df_nosioci, novi_red], ignore_index=False)
                sacuvaj_bazu(df_nosioci, 'NOSIOCI')
                st.success("Zaduženje upisano!")
                st.rerun()
    st.write("")
    edited_df = st.data_editor(df_nosioci, use_container_width=True, num_rows="dynamic", key="editor_nosioci")
    if edited_df is not None and not edited_df.equals(df_nosioci):
        sacuvaj_bazu(edited_df, 'NOSIOCI')
        st.rerun()

elif modul == "ISPRAVNOST":
    prikazi_ispravnost(fajl_baze)

elif modul == "RASPORED":
    prikazi_raspored(fajl_baze)
