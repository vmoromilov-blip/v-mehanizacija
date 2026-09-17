import streamlit as st
import pandas as pd
import os
from datetime import datetime

def prikazi_nosioce(fajl_baze):
    fajl_csv = "nosioci_baza.csv"
    
    # Ako živa baza u fascikli još ne postoji, pravimo je iz Excela
    if not os.path.exists(fajl_csv) or os.path.getsize(fajl_csv) == 0:
        if os.path.exists(fajl_baze):
            try:
                df = pd.read_excel(fajl_baze, sheet_name='NOSIOCI')
                if 'START DATUM' in df.columns:
                    df['START DATUM'] = pd.to_datetime(df['START DATUM']).dt.strftime('%d.%m.%Y')
                df.to_csv(fajl_csv, index=False)
            except:
                df = pd.DataFrame(columns=['ID MAŠINE', 'TIP TURNUSA', 'START DATUM', 'SMENA', 'ID BROJ', 'NOSILAC'])
        else:
            df = pd.DataFrame(columns=['ID MAŠINE', 'TIP TURNUSA', 'START DATUM', 'SMENA', 'ID BROJ', 'NOSILAC'])
            df.to_csv(fajl_csv, index=False)

    try:
        df = pd.read_csv(fajl_csv)
    except:
        return

    # 🎯 AUTOMATSKO SORTIRANJE OD A DO Z PO GARAŽNOM BROJU
    if 'ID MAŠINE' in df.columns:
        df = df.sort_values(by='ID MAŠINE').reset_index(drop=True)

    df = df.rename(columns={'DATUM POČETKA': 'START DATUM', 'SAP BROJ': 'ID BROJ'})
    if 'TIP' in df.columns:
        df = df.drop(columns=['TIP'], errors='ignore')

    df = df.fillna('')

    # Učitavamo spiskove za padajuće menije
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

    # --- KRUPNO OBLAČNO DUGME NA VRHU ---
    with st.popover("🔑 DODAJ NOSIOCA"):
        st.write("### Unesi novo zaduženje mehanizacije")
        n_id = st.selectbox("Izaberi garažni broj mašine:", opcije_masina, key="nos_id")
        n_turnus = st.selectbox("Tip turnusa (Način rada):", ["1", "5", "7", "15", "30"], key="nos_tur")
        n_smena = st.radio("Smena:", ["A", "B"], horizontal=True, key="nos_sme")
        n_radnik = st.selectbox("Izaberi stalnog nosioca (vozača):", opcije_radnika, key="nos_rad")
        n_datum = st.date_input("Datum starta turnusa:", datetime.now().date(), key="nos_dat")
        
        if st.button("SAČUVAJ ZADUŽENJE", key="nos_btn"):
            if n_id and n_radnik:
                id_br = ""
                if os.path.exists('POSADA_BAZA.csv'):
                    df_r = pd.read_csv('POSADA_BAZA.csv')
                    s = df_r[df_r['PREZIME I IME'] == n_radnik]['SAP BROJ'].values
                    try:
                        id_br = str(int(float(s))) if len(s) > 0 and pd.notna(s) else ""
                    except:
                        id_br = str(s) if len(s) > 0 else ""

                novi_red = {
                    'ID MAŠINE': str(n_id).strip().upper(),
                    'TIP TURNUSA': str(n_turnus),
                    'START DATUM': n_datum.strftime('%d.%m.%Y'),
                    'SMENA': str(n_smena).strip().upper(),
                    'ID BROJ': id_br,
                    'NOSILAC': n_radnik
                }
                df = pd.concat([df, pd.DataFrame([novi_red])], ignore_index=True)
                df.to_csv(fajl_csv, index=False)
                st.success("Zaduženje upisano u fasciklu!")
                st.rerun()

    st.write("")

    for col in ['ID BROJ', 'TIP TURNUSA']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.replace('nan', '').str.strip()

    # 🎯 POTPUNO OTKLJUČANA I ŠIROKA TABELA OD IVICE DO IVICE EKRANA
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "ID MAŠINE": st.column_config.SelectboxColumn("ID MAŠINE", options=opcije_masina, pinned=True, width="small"),
            "TIP TURNUSA": st.column_config.SelectboxColumn("TIP TURNUSA", options=["1", "5", "7", "15", "30"], width="small"),
            "START DATUM": st.column_config.TextColumn("START DATUM", width="medium"),
            "SMENA": st.column_config.SelectboxColumn("SMENA", options=["A", "B"], width="small"),
            "ID BROJ": st.column_config.TextColumn("ID BROJ", width="small"),
            "NOSILAC": st.column_config.SelectboxColumn("NOSILAC", options=opcije_radnika, width="large")
        },
        key="zivi_editor_nosilaca_finalni_otkljucani"
    )
    
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
