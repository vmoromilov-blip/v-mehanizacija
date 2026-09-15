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
        if st.button("🗑️ Obriši selektovane mašine"):
            st.info("Štiklirajte redove levo u tabeli i pritisnite ikonicu kante u tabeli ispod.")
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
                if Server_ime:
                    novi_red = pd.DataFrame([{'SAP BROJ': novi_sap, 'PREZIME I IME': novo_ime.upper(), 'STATUS': 'AKTIVAN'}])
                    df_radnici = pd.concat([df_radnici, novi_red], ignore_index=False)
                    sacuvaj_bazu(df_radnici, 'SPISAK RADNIKA')
                    st.success("Radnik upisan!")
                    st.rerun()
    with col2:
        if st.button("🗑️ Obriši selektovane radnike"):
            st.info("Štiklirajte kućicu levo pored radnika i upotrebite ikonicu kante u tabeli ispod.")

    st.write("")
    edited_df = st.data_editor(df_radnici, use_container_width=True, num_rows="dynamic", key="editor_radnici")
    if edited_df is not None and not edited_df.equals(df_radnici):
        sacuvaj_bazu(edited_df, 'SPISAK RADNIKA')
        st.rerun()

elif modul == "ZAMENA":
    st.write("## 🔄 Spisak i evidencija zamena")
    df_zamena = ucitaj_ili_napravi_bazu('ZAMENA', ['ID MAŠINE', 'SMENA', 'ODSUTAN RADNIK', 'SAP BROJ', 'DATUM POČETKA', 'DATUM ZAVRŠETKA', 'SAP BROJ.1', 'ZAMENA'])
    df_zamena = df_zamena.rename(columns={'START DATUM': 'DATUM POČETKA', 'END DATUM': 'DATUM ZAVRŠETKA'})
    
    for col in ['DATUM POČETKA', 'DATUM ZAVRŠETKA']:
        if col in df_zamena.columns:
            df_zamena[col] = pd.to_datetime(df_zamena[col]).dt.date

    # Učitavamo spisak radnika iz fascikle da bismo znali njihove SAP brojeve
    df_svi_radnici = ucitaj_ili_napravi_bazu('SPISAK RADNIKA', ['SAP BROJ', 'PREZIME I IME', 'STATUS'])

    col1, col2 = st.columns(2)
    with col1:
        with st.popover("➕ Dodaj zamenu"):
            st.write("### Unesi podatke za novu zamenu")
            z_id = st.text_input("Garažni broj mašine:")
            z_smena = st.text_input("Smena:")
            
            # Umesto kucanja, biramo ljude iz padajuće liste postojećih radnika!
            lista_radnika = sorted(df_svi_radnici['PREZIME I IME'].dropna().unique())
            z_odsutan = st.selectbox("Izaberi odsutnog radnika:", lista_radnika)
            z_zamena = st.selectbox("Izaberi radnika koji menja (ZAMENA):", lista_radnika)
            
            z_pocetak = st.date_input("Datum početka:")
            z_zavrsetak = st.date_input("Datum završetka:")
            
            if st.button("Sačuvaj zamenu"):
                # AUTOMATSKI PRONALAZIMO SAP BROJEVE ZA OBA RADNIKA
                sap_odsutnog = df_svi_radnici[df_svi_radnici['PREZIME I IME'] == z_odsutan]['SAP BROJ'].values
                sap_zamene = df_svi_radnici[df_svi_radnici['PREZIME I IME'] == z_zamena]['SAP BROJ'].values
                
                br_odsutan = sap_odsutnog[0] if len(sap_odsutnog) > 0 else ""
                br_zamena = sap_zamene[0] if len(sap_zamene) > 0 else ""
                
                # Dinamički proveravamo nazive kolona u tvom Excelu da upišemo na pravo mesto
                kolone_u_bazi = list(df_zamena.columns)
                sap_ods_col = 'SAP BROJ' if 'SAP BROJ' in kolone_u_bazi else kolone_u_bazi[3]
                sap_zam_col = 'SAP BROJ.1' if 'SAP BROJ.1' in kolone_u_bazi else kolone_u_bazi[6]
                
                novi_red = pd.DataFrame([{
                    'ID MAŠINE': z_id.upper(), 
                    'SMENA': z_smena.upper(),
                    'ODSUTAN RADNIK': z_odsutan, 
                    sap_ods_col: br_odsutan,
                    'DATUM POČETKA': str(z_pocetak),
                    'DATUM ZAVRŠETKA': str(z_zavrsetak), 
                    sap_zam_col: br_zamena,
                    'ZAMENA': z_zamena
                }])
                
                df_zamena = pd.concat([df_zamena, novi_red], ignore_index=False)
                sacuvaj_bazu(df_zamena, 'ZAMENA')
                st.success("Zamena upisana i SAP brojevi automatski povučeni!")
                st.rerun()
    with col2:
        if st.button("🗑️ Obriši selektovane zamene"):
            st.info("Štiklirajte redove levo u tabeli i upotrebite ikonicu kante u tabeli ispod.")
                
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
