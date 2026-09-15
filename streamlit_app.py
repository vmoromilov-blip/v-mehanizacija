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

# Pomoćne funkcije za trajno čuvanje u lokalnim CSV datotekama unutar naše internet fascikle
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
                    st.success("Mašina trajno upisana u fasciklu!")
                    st.rerun()
    with col2:
        if st.button("🗑️ Obriši selektovane mašine"):
            st.info("Štiklirajte redove direktno u tabeli ispod, pritisnite taster Delete na tastaturi ili ikonicu kante, a zatim će sistem automatski zapamtiti izmene.")

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
                    st.success("Radnik trajno upisan u fasciklu!")
                    st.rerun()
    with col2:
        if st.button("🗑️ Obriši selektovane radnike"):
            st.info("Označite radnika kućicom skroz levo u tabeli i upotrebite ikonicu kante za trajno uklanjanje.")

    st.write("")
    edited_df = st.data_editor(df_radnici, use_container_width=True, num_rows="dynamic", key="editor_radnici")
    if edited_df is not None and not edited_df.equals(df_radnici):
        sacuvaj_bazu(edited_df, 'SPISAK RADNIKA')
        st.rerun()

elif modul == "ZAMENA":
    st.write("## 🔄 Spisak i evidencija zamena")
    if os.path.exists(fajl_baze):
        df_zamena = pd.read_excel(fajl_baze, sheet_name='ZAMENA')
        df_zamena = df_zamena.rename(columns={'START DATUM': 'DATUM POČETKA', 'END DATUM': 'DATUM ZAVRŠETKA'})
        if 'DATUM POČETKA' in df_zamena.columns:
            df_zamena['DATUM POČETKA'] = pd.to_datetime(df_zamena['DATUM POČETKA']).dt.date
        if 'DATUM ZAVRŠETKA' in df_zamena.columns:
            df_zamena['DATUM ZAVRŠETKA'] = pd.to_datetime(df_zamena['DATUM ZAVRŠETKA']).dt.date
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
    # PREBACUJEMO I NOSIOCE NA TRAJNU LOKALNU BAZU U FASCIKLI
    df_nosioci = ucitaj_ili_napravi_bazu('NOSIOCI', ['ID MAŠINE', 'TIP TURNUSA', 'DATUM POČETKA', 'SMENA', 'SAP BROJ', 'NOSILAC'])
    
    if 'TIP' in df_nosioci.columns:
        df_nosioci = df_nosioci.drop(columns=['TIP'], errors='ignore')
    df_nosioci = df_nosioci.rename(columns={'START DATUM': 'DATUM POČETKA'})

    col1, col2 = st.columns(2)
    with col1:
        with st.popover("➕ Dodaj nosioca"):
            st.write("### Unesi zaduženje mehanizacije")
            novi_id = st.text_input("Garažni broj mašine (ID MAŠINE):")
            novi_turnus = st.text_input("Tip turnusa (npr. 1 ili 5):")
            nova_smena = st.text_input("Smena (npr. A ili B):")
            novi_sap_br = st.text_input("SAP Broj radnika:")
            novi_nosilac_ime = st.text_input("Prezime i ime radnika (NOSILAC):")
            
            if st.button("Sačuvaj zaduženje"):
                if novi_id and novi_nosilac_ime:
                    novi_red = pd.DataFrame([{
                        'ID MAŠINE': novi_id.upper(),
                        'TIP TURNUSA': novi_turnus,
                        'DATUM POČETKA': datetime.now().strftime('%Y-%m-%d'),
                        'SMENA': nova_smena.upper(),
                        'SAP BROJ': novi_sap_br,
                        'NOSILAC': novi_nosilac_ime.upper()
                    }])
                    df_nosioci = pd.concat([df_nosioci, novi_red], ignore_index=False)
                    sacuvaj_bazu(df_nosioci, 'NOSIOCI')
                    st.success("Zaduženje uspešno i trajno zabeleženo u fascikli!")
                    st.rerun()
    with col2:
        if st.button("🗑️ Raskini selektovana zaduženja"):
            st.info("Štiklirajte kućicu skroz levo pored zaduženja koje želite da obrišete i kliknite na kantu u tabeli ispod.")

    st.write("")
    edited_df = st.data_editor(df_nosioci, use_container_width=True, num_rows="dynamic", key="editor_nosioci")
    if edited_df is not None and not edited_df.equals(df_nosioci):
        sacuvaj_bazu(edited_df, 'NOSIOCI')
        st.rerun()

elif modul == "ISPRAVNOST":
    prikazi_ispravnost(fajl_baze)

elif modul == "RASPORED":
    prikazi_raspored(fajl_baze)
