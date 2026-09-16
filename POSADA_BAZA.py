import streamlit as st
import pandas as pd
import os

def prikazi_posadu(fajl_baze):
    fajl_csv = "POSADA_BAZA.csv"
    
    # Ako fajl u fascikli već postoji, obrisaćemo ga da povučemo sveže podatke bez greške
    if os.path.exists(fajl_csv):
        try:
            os.remove(fajl_csv)
        except:
            pass
            
    if os.path.exists(fajl_baze):
        try:
            # Čitamo tačan šit iz Excela kako god da su kolone napisane
            df = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
            df.to_csv(fajl_csv, index=False)
        except:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    if not df.empty:
        # Čistimo višak starih kolona ako postoje
        if 'EMAIL ADRESA' in df.columns:
            df = df.drop(columns=['EMAIL ADRESA', 'TIP', 'Unnamed: 3'], errors='ignore')

        # Čisto dugme na vrhu
        with st.popover("➕ DODAJ RADNIKA"):
            st.write("### Unesi novog radnika u sistem")
            novo_ime = st.text_input("Prezime i ime radnika:")
            novi_sap = st.text_input("SAP broj radnika:")
            if st.button("SAČUVAJ U VOZAČE"):
                if novo_ime:
                    # Gledamo kako se zovu prve tri kolone u tvom Excelu da upišemo na pravo mesto
                    kolone = list(df.columns)
                    novi_red = {kolone[0]: novi_sap.strip(), kolone[1]: novo_ime.upper().strip()}
                    if len(kolone) > 2:
                        novi_red[kolone[2]] = 'AKTIVAN'
                    
                    df = pd.concat([df, pd.DataFrame([novi_red])], ignore_index=True)
                    df.to_csv(fajl_csv, index=False)
                    st.success("Radnik uspešno upisan!")
                    st.rerun()
                        
        st.write("")

        # Otvaramo čistu tabelu bez ručnog kucanja imena kolona da ne može da pukne
        izmenjeni_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            key="zivi_editor_radnika_finalni_najsigurniji"
        )
        
        if izmenjeni_df is not None and not izmenjeni_df.equals(df):
            izmenjeni_df.to_csv(fajl_csv, index=False)
            st.rerun()
    else:
        st.error("Podaci iz šita 'SPISAK RADNIKA' nisu uspešno učitani.")
