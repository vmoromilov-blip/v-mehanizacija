import streamlit as st
import pandas as pd
import os
from datetime import datetime

def prikazi_zamenu(fajl_baze):
    fajl_csv = "zamena.csv"
    
    # 🚀 REVOLUCIONARNO ČIŠĆENJE: Prisilno brišemo stari fajl iz memorije ako je povukao loše kolone
    if os.path.exists(fajl_csv):
        try:
            df_provera = pd.read_csv(fajl_csv)
            if 'SAP BROJ' in df_provera.columns or df_provera.empty:
                os.remove(fajl_csv)
        except:
            os.remove(fajl_csv)

    # Ako fajl u fascikli ne postoji, pravimo ga iz Excela potpuno čistog
    if not os.path.exists(fajl_csv) or os.path.getsize(fajl_csv) == 0:
        if os.path.exists(fajl_baze):
            try:
                df = pd.read_excel(fajl_baze, sheet_name='ZAMENA')
                # Sređujemo datume na samom startu
                for col in ['DATUM POČETKA', 'DATUM ZAVRŠETKA', 'START DATUM', 'END DATUM']:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col]).dt.strftime('%d.%m.%Y')
                
                # Preimenujemo stare kolone iz Excela u naša nova operativna imena
                df = df.rename(columns={
                    'START DATUM': 'DATUM POČETKA', 
                    'END DATUM': 'DATUM ZAVRŠETKA',
                    'SAP BROJ': 'ID BROJ',
                    'SAP BROJ.1': 'ID BROJ 2',
                    'SAP BROJ2': 'ID BROJ 2'
                })
                df.to_csv(fajl_csv, index=False)
            except:
                df = pd.DataFrame(columns=['ID MAŠINE', 'SMENA', 'ODSUTAN RADNIK', 'ID BROJ', 'DATUM POČETKA', 'DATUM ZAVRŠETKA', 'ID BROJ 2', 'ZAMENA'])
                df.to_csv(fajl_csv, index=False)
        else:
            df = pd.DataFrame(columns=['ID MAŠINE', 'SMENA', 'ODSUTAN RADNIK', 'ID BROJ', 'DATUM POČETKA', 'DATUM ZAVRŠETKA', 'ID BROJ 2', 'ZAMENA'])
            df.to_csv(fajl_csv, index=False)

    try:
        df = pd.read_csv(fajl_csv)
    except:
        return

    # Osiguravamo nova imena kolona u tabeli
    df = df.rename(columns={
        'SAP BROJ': 'ID BROJ',
        'SAP BROJ.1': 'ID BROJ 2',
        'SAP BROJ2': 'ID BROJ 2',
        'ID BROJ.1': 'ID BROJ 2'
    })

    # Čistimo zareze i decimale na svim ID kolonama koje postoje u bazi
    for col in df.columns:
        if 'ID BROJ' in str(col).upper():
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.replace('nan', '').str.strip()

    df = df.fillna('')

    # Učitavamo živu listu radnika i mašina za padajuće menije
    opcije_radnika = [""]
    if os.path.exists('POSADA_BAZA.csv'):
        try:
            df_r = pd.read_csv('POSADA_BAZA.csv')
            if 'PREZIME I IME' in df_r.columns:
                opcije_radnika.extend(sorted(df_r['PREZIME I IME'].dropna().astype(str).unique()))
        except:
            pass

    opcije_masina = [""]
    if os.path.exists('GARAZA_BAZA.csv'):
        try:
            df_m = pd.read_csv('GARAZA_BAZA.csv')
            if 'GARAŽNI BROJ' in df_m.columns:
                opcije_masina.extend(sorted(df_m['GARAŽNI BROJ'].dropna().astype(str).unique()))
        except:
            pass

    # --- KONTROLNO DUGME NA VRHU EKRAZA ---
    with st.popover("🔄 DODAJ ZAMENU"):
        st.write("### Unesi novu vojnu naredbu o zameni")
        z_id = st.selectbox("Izaberi garažni broj mašine:", opcije_masina)
        z_smena = st.radio("Smena:", ["A", "B"], horizontal=True)
        z_odsutan = st.selectbox("Izaberi odsutnog radnika:", opcije_radnika)
        z_zamena = st.selectbox("Izaberi radnika koji ga menja (ZAMENA):", opcije_radnika)
        z_pocetak = st.date_input("Datum početka zamene:")
        z_zavrsetak = st.date_input("Datum završetka zamene:")
        
        if st.button("UPREGLI I SAČUVAJ ZAMENU"):
            if z_id and z_odsutan and z_zamena:
                sap_odsutnog = ""
                sap_zamene = ""
                if os.path.exists('POSADA_BAZA.csv'):
                    df_r = pd.read_csv('POSADA_BAZA.csv')
                    s1 = df_r[df_r['PREZIME I IME'] == z_odsutan]['SAP BROJ'].values
                    s2 = df_r[df_r['PREZIME I IME'] == z_zamena]['SAP BROJ'].values
                    sap_odsutnog = str(int(float(s1[0]))) if len(s1) > 0 and pd.notna(s1[0]) else ""
                    sap_zamene = str(int(float(s2[0]))) if len(s2) > 0 and pd.notna(s2[0]) else ""

                novi_red = pd.DataFrame([{
                    'ID MAŠINE': str(z_id).strip().upper(),
                    'SMENA': str(z_smena).strip().upper(),
                    'ODSUTAN RADNIK': z_odsutan,
                    'ID BROJ': sap_odsutnog,
                    'DATUM POČETKA': z_pocetak.strftime('%d.%m.%Y'),
                    'DATUM ZAVRŠETKA': z_zavrsetak.strftime('%d.%m.%Y'),
                    'ID BROJ 2': sap_zamene,
                    'ZAMENA': z_zamena
                }])
                df = pd.concat([df, novi_red], ignore_index=True)
                df.to_csv(fajl_csv, index=False)
                st.success("Zamena uspešno zavedena!")
                st.rerun()
                
    st.write("")

    # Konfiguracija kolona sa novim nazivima i zaključanim pinom
    konfig = {
        "ID MAŠINE": st.column_config.SelectboxColumn("ID MAŠINE", options=opcije_masina, pinned=True, width="small"),
        "SMENA": st.column_config.SelectboxColumn("SMENA", options=["A", "B"], width="small"),
        "ODSUTAN RADNIK": st.column_config.SelectboxColumn("ODSUTAN RADNIK", options=opcije_radnika, width="medium"),
        "ID BROJ": st.column_config.TextColumn("ID BROJ", width="small", disabled=True),
        "DATUM POČETKA": st.column_config.TextColumn("DATUM POČETKA", width="medium"),
        "DATUM ZAVRŠETKA": st.column_config.TextColumn("DATUM ZAVRŠETKA", width="medium"),
        "ID BROJ 2": st.column_config.TextColumn("ID BROJ 2", width="small", disabled=True),
        "ZAMENA": st.column_config.SelectboxColumn("ZAMENA", options=opcije_radnika, width="medium")
    }

    # Prikazujemo fiksiranu, široku tabelu zamena od ivice do ivice
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config=konfig,
        key="zivi_editor_zamena_finalni_mirni"
    )
    
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
