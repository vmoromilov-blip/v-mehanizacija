import streamlit as st
import pandas as pd
import os
from datetime import datetime

def prikazi_zamenu(fajl_baze):
    fajl_csv = "zamena.csv"
    
    # Ako živa baza u fascikli još ne postoji, pravimo je iz Excela
    if not os.path.exists(fajl_csv) or os.path.getsize(fajl_csv) == 0:
        if os.path.exists(fajl_baze):
            try:
                df = pd.read_excel(fajl_baze, sheet_name='ZAMENA')
                # Prilagođavamo datume da odmah budu u lepom formatu
                for col in ['DATUM POČETKA', 'DATUM ZAVRŠETKA', 'START DATUM', 'END DATUM']:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col]).dt.strftime('%d.%m.%Y')
                df = df.rename(columns={'START DATUM': 'DATUM POČETKA', 'END DATUM': 'DATUM ZAVRŠETKA'})
                df.to_csv(fajl_csv, index=False)
            except:
                df = pd.DataFrame(columns=['ID MAŠINE', 'SMENA', 'ODSUTAN RADNIK', 'SAP BROJ', 'DATUM POČETKA', 'DATUM ZAVRŠETKA', 'SAP BROJ.1', 'ZAMENA'])
        else:
            df = pd.DataFrame(columns=['ID MAŠINE', 'SMENA', 'ODSUTAN RADNIK', 'SAP BROJ', 'DATUM POČETKA', 'DATUM ZAVRŠETKA', 'SAP BROJ.1', 'ZAMENA'])
            df.to_csv(fajl_csv, index=False)

    try:
        df = pd.read_csv(fajl_csv)
    except:
        return

    df = df.fillna('')

    # Učitavamo živu listu radnika i mašina iz ostalih fascikli za padajuće menije
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

    # --- KONTROLNO DUGME SKROZ LEVO U ISTOJ LINIJI ---
    col_dugme, col_prazno = st.columns(2)
    
    with col_dugme:
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
                    # Izvlačimo sap brojeve automatski iz posade da ih ne kucaš pešaka
                    sap_odsutnog = ""
                    sap_zamene = ""
                    if os.path.exists('POSADA_BAZA.csv'):
                        df_r = pd.read_csv('POSADA_BAZA.csv')
                        s1 = df_r[df_r['PREZIME I IME'] == z_odsutan]['SAP BROJ'].values
                        s2 = df_r[df_r['PREZIME I IME'] == z_zamena]['SAP BROJ'].values
                        sap_odsutnog = str(s1[0]) if len(s1) > 0 else ""
                        sap_zamene = str(s2[0]) if len(s2) > 0 else ""

                    novi_red = pd.DataFrame([{
                        'ID MAŠINE': str(z_id).strip().upper(),
                        'SMENA': str(z_smena).strip().upper(),
                        'ODSUTAN RADNIK': z_odsutan,
                        'SAP BROJ': sap_odsutnog,
                        'DATUM POČETKA': z_pocetak.strftime('%d.%m.%Y'),
                        'DATUM ZAVRŠETKA': z_zavrsetak.strftime('%d.%m.%Y'),
                        'SAP BROJ.1': sap_zamene,
                        'ZAMENA': z_zamena
                    }])
                    df = pd.concat([df, novi_red], ignore_index=True)
                    df.to_csv(fajl_csv, index=False)
                    st.success("Zamena uspešno zavedena u sistem!")
                    st.rerun()
                    
    st.write("")

    # Konfiguracija za komforan pregled i padajuće menije na dvoklik unutar ćelija
    konfig = {
        "ID MAŠINE": st.column_config.SelectboxColumn("ID MAŠINE", options=opcije_masina, pinned=True, width="small"),
        "SMENA": st.column_config.SelectboxColumn("SMENA", options=["A", "B"], width="small"),
        "ODSUTAN RADNIK": st.column_config.SelectboxColumn("ODSUTAN RADNIK", options=opcije_radnika, width="medium"),
        "SAP BROJ": st.column_config.TextColumn("SAP BROJ", width="small", disabled=True),
        "DATUM POČETKA": st.column_config.TextColumn("DATUM POČETKA", width="medium"),
        "DATUM ZAVRŠETKA": st.column_config.TextColumn("DATUM ZAVRŠETKA", width="medium"),
        "SAP BROJ.1": st.column_config.TextColumn("SAP BROJ.1", width="small", disabled=True),
        "ZAMENA": st.column_config.SelectboxColumn("ZAMENA", options=opcije_radnika, width="medium")
    }

    # Prikazujemo fiksiranu, široku tabelu zamena od ivice do ivice
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config=konfig,
        key="zivi_editor_zamena_finalni"
    )
    
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
