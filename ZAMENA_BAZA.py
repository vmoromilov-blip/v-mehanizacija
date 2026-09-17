import streamlit as st
import pandas as pd
import os
from ZAMENA_MATEMATIKA import ocisti_decimale_i_kolone, nadji_id_broj_radnika

def prikazi_zamenu(fajl_baze):
    fajl_csv = "zamena.csv"
    
    if not os.path.exists(fajl_csv) or os.path.getsize(fajl_csv) == 0:
        if os.path.exists(fajl_baze):
            df = pd.read_excel(fajl_baze, sheet_name='ZAMENA')
            df.to_csv(fajl_csv, index=False)
        else:
            st.error("Glavni Excel fajl 'plan.xlsm' nije pronađen.")
            return

    try:
        df = pd.read_csv(fajl_csv)
    except:
        return

    df = ocisti_decimale_i_kolone(df)

    # 🎯 AUTOMATSKO SORTIRANJE OD A DO Z PO GARAŽNOM BROJU MAŠINE
    if 'ID MAŠINE' in df.columns:
        df = df.sort_values(by='ID MAŠINE').reset_index(drop=True)

    opcije_radnika = [""]
    if os.path.exists('POSADA_BAZA.csv'):
        opcije_radnika.extend(sorted(pd.read_csv('POSADA_BAZA.csv')['PREZIME I IME'].dropna().unique()))
        
    opcije_masina = [""]
    if os.path.exists('GARAZA_BAZA.csv'):
        opcije_masina.extend(sorted(pd.read_csv('GARAZA_BAZA.csv')['GARAŽNI BROJ'].dropna().unique()))

    with st.popover("🔄 DODAJ ZAMENU"):
        z_id = st.selectbox("Izaberi garažni broj mašine:", opcije_masina)
        z_smena = st.radio("Smena:", ["A", "B"], horizontal=True)
        z_odsutan = st.selectbox("Izaberi odsutnog radnika:", opcije_radnika)
        z_zamena = st.selectbox("Izaberi radnika koji ga menja:", opcije_radnika)
        z_pocetak = st.date_input("Datum početka zamene:")
        z_zavrsetak = st.date_input("Datum završetka zamene:")
        
        if st.button("UPREGLI I SAČUVAJ ZAMENU"):
            if z_id and z_odsutan and z_zamena:
                novi_red = pd.DataFrame([{
                    'ID MAŠINE': str(z_id).strip().upper(), 'SMENA': str(z_smena).strip().upper(),
                    'ODSUTAN RADNIK': z_odsutan, 'ID BROJ': nadji_id_broj_radnika(z_odsutan),
                    'DATUM POČETKA': z_pocetak.strftime('%d.%m.%Y'), 'DATUM ZAVRŠETKA': z_zavrsetak.strftime('%d.%m.%Y'),
                    'ID BROJ 2': nadji_id_broj_radnika(z_zamena), 'ZAMENA': z_zamena
                }])
                df = pd.concat([df, novi_red], ignore_index=True)
                df.to_csv(fajl_csv, index=False)
                st.success("Zamena uspešno zavedena!")
                st.rerun()

    st.write("")

    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "ID MAŠINE": st.column_config.SelectboxColumn("ID MAŠINE", options=opcije_masina, pinned=True, width="small"),
            "SMENA": st.column_config.SelectboxColumn("SMENA", options=["A", "B"], width="small"),
            "ODSUTAN RADNIK": st.column_config.SelectboxColumn("ODSUTAN RADNIK", options=opcije_radnika, width="medium"),
            "ID BROJ": st.column_config.TextColumn("ID BROJ", width="small", disabled=True),
            "ID BROJ 2": st.column_config.TextColumn("ID BROJ 2", width="small", disabled=True),
            "ZAMENA": st.column_config.SelectboxColumn("ZAMENA", options=opcije_radnika, width="medium")
        },
        key="zivi_editor_zamena_finalni_mirni"
    )
    
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
