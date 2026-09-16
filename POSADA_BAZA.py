import streamlit as st
import pandas as pd
import os

def prikazi_posadu(fajl_baze):
    fajl_csv = "POSADA_BAZA.csv"
    
    # Čitamo iz Excela SAMO ako fajl u fascikli već ne postoji (ovo leči treptanje!)
    if not os.path.exists(fajl_csv) or os.path.getsize(fajl_csv) == 0:
        if os.path.exists(fajl_baze):
            try:
                df = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
                # Čistimo prazna mesta u nazivima kolona
                df.columns = [str(c).strip() for c in df.columns]
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

    # Čistimo višak starih kolona ako postoje
    if 'EMAIL ADRESA' in df.columns:
        df = df.drop(columns=['EMAIL ADRESA', 'TIP', 'Unnamed: 3'], errors='ignore')

    # Čisto i bezbedno dugme na vrhu
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

    # 🎯 TRAJNO CEMENTIRAMO I PIN I ŠIRINE KOLONA (BEZ TREPTANJA)
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "SAP BROJ": st.column_config.TextColumn(
                "SAP BROJ", 
                pinned=True,     # ZAKLJUČAN PIN!
                width="small"
            ),
            "PREZIME I IME": st.column_config.TextColumn(
                "PREZIME I IME", 
                width="large"    # ŠIROKA KOLONA ZA IMENA
            ),
            "STATUS": st.column_config.TextColumn(
                "STATUS", 
                width="medium"
            )
        },
        key="zivi_editor_radnika_finalni_sigurni_mirni"
    )
    
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
