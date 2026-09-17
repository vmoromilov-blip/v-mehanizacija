import streamlit as st
import pandas as pd
import os

def prikazi_posadu(fajl_baze):
    fajl_csv = "POSADA_BAZA.csv"
    
    if not os.path.exists(fajl_csv) or os.path.getsize(fajl_csv) == 0:
        if os.path.exists(fajl_baze):
            try:
                df = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
                df.to_csv(fajl_csv, index=False)
            except:
                df = pd.DataFrame(columns=['SAP BROJ', 'PREZIME I IME', 'STATUS'])
                df.to_csv(fajl_csv, index=False)
        else:
            df = pd.DataFrame(columns=['SAP BROJ', 'PREZIME I IME', 'STATUS'])
            df.to_csv(fajl_csv, index=False)

    try:
        df = pd.read_csv(fajl_csv)
    except:
        return

    # 🎯 AUTOMATSKO SORTIRANJE OD A DO Z PO PREZIMENU I IMENU VOZAČA
    if 'PREZIME I IME' in df.columns:
        df = df.sort_values(by='PREZIME I IME').reset_index(drop=True)

    with st.popover("➕ DODAJ RADNIKA"):
        st.write("### Unesi novog radnika u sistem")
        novo_ime = st.text_input("Prezime i ime radnika:")
        novi_sap = st.text_input("SAP broj radnika:")
        if st.button("SAČUVAJ U VOZAČE"):
            if novo_ime:
                novi_red = pd.DataFrame([{'SAP BROJ': novi_sap.strip(), 'PREZIME I IME': novo_ime.upper().strip(), 'STATUS': 'AKTIVAN'}])
                df = pd.concat([df, novi_red], ignore_index=True)
                df.to_csv(fajl_csv, index=False)
                st.success("Radnik uspešno upisan!")
                st.rerun()
                    
    st.write("")

    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "SAP BROJ": st.column_config.TextColumn("SAP BROJ", pinned=True, width="small"),
            "PREZIME I IME": st.column_config.TextColumn("PREZIME I IME", width="large"),
            "STATUS": st.column_config.TextColumn("STATUS", width="medium")
        },
        key="zivi_editor_radnika_cist_i_siguran"
    )
    
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
