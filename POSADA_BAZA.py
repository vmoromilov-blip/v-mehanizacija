import streamlit as st
import pandas as pd
import os

def prikazi_posadu(fajl_baze):
    fajl_csv = "POSADA_BAZA.csv"
    
    # Prisilno čistimo stari fajl da povučemo čistu strukturu
    if os.path.exists(fajl_csv):
        try:
            os.remove(fajl_csv)
        except:
            pass
            
    if os.path.exists(fajl_baze):
        try:
            df = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
            # Čistimo prazne redove i kolone ako ih ima na dnu
            df = df.dropna(how='all')
            df.to_csv(fajl_csv, index=False)
        except:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    if not df.empty:
        # Čistimo višak starih kolona ako slučajno postoje
        if 'EMAIL ADRESA' in df.columns:
            df = df.drop(columns=['EMAIL ADRESA', 'TIP', 'Unnamed: 3'], errors='ignore')

        # Čisto fabričko dugme na vrhu ekrana
        with st.popover("➕ DODAJ RADNIKA"):
            st.write("### Unesi novog radnika u sistem")
            novo_ime = st.text_input("Prezime i ime radnika:")
            novi_sap = st.text_input("SAP broj radnika:")
            if st.button("SAČUVAJ U VOZAČE"):
                if novo_ime:
                    kolone = list(df.columns)
                    novi_red = {kolone[0]: novi_sap.strip(), kolone[1]: novo_ime.upper().strip()}
                    if len(kolone) > 2:
                        novi_red[kolone[2]] = 'AKTIVAN'
                    
                    df = pd.concat([df, pd.DataFrame([novi_red])], ignore_index=True)
                    df.to_csv(fajl_csv, index=False)
                    st.success("Radnik uspešno upisan!")
                    st.rerun()
                        
        st.write("")

        # 🎯 AUTOMATSKI PIN ZA PRVU KOLONU KAKO GOD DA SE ONA ZOVE U EXCELU
        kolone_baze = list(df.columns)
        konfig = {}
        if len(kolone_baze) > 0:
            konfig[kolone_baze[0]] = st.column_config.TextColumn(kolone_baze[0], pinned=True, width="small")
        if len(kolone_baze) > 1:
            konfig[kolone_baze[1]] = st.column_config.TextColumn(kolone_baze[1], width="large")

        # Pokrećemo potpuno stabilan editor bez ijednog tvrdog naziva kolone
        izmenjeni_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            column_config=konfig,
            key="zivi_editor_radnika_konacni_otporni"
        )
        
        if izmenjeni_df is not None and not izmenjeni_df.equals(df):
            izmenjeni_df.to_csv(fajl_csv, index=False)
            st.rerun()
    else:
        st.error("Podaci iz šita 'SPISAK RADNIKA' nisu pronađeni u Excelu.")
