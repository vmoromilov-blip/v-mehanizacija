import streamlit as st
import pandas as pd
import os

def prikazi_posadu(fajl_baze):
    fajl_csv = "POSADA_BAZA.csv"
    
    # 🎯 LEK PROTIV TREPTANJA: Čitamo iz Excela SAMO ako brza baza u fascikli ne postoji
    if not os.path.exists(fajl_csv) or os.path.getsize(fajl_csv) == 0:
        if os.path.exists(fajl_baze):
            try:
                df = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
                df.columns = [str(c).strip() for c in df.columns]
                
                # Izbacujemo nepotrebne kolone odmah na početku
                kolone_za_brisanje = ['EMAIL ADRESA', 'TIP', 'Unnamed: 3']
                df = df.drop(columns=[c for c in kolone_za_brisanje if c in df.columns], errors='ignore')
                
                # Popunjavamo status
                df['STATUS'] = 'AKTIVAN'
                
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

    # 🎯 AUTOMATSKO SORTIRANJE OD A DO Z PO DRUGOJ KOLONI (PREZIME I IME)
    if len(df.columns) > 1:
        kolona_za_sort = df.columns[1]
        df = df.sort_values(by=kolona_za_sort).reset_index(drop=True)

    # Čisto fabričko dugme na samom vrhu ekrana
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

    # Mirna i stabilna tabela od ivice do ivice ekrana koja nikada više ne trepće
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        key="zivi_editor_radnika_konacni_stopostotni"
    )
    
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
