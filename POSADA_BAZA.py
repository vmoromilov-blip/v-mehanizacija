import streamlit as st
import pandas as pd
import os

def prikazi_posadu(fajl_baze):
    # Cementiramo vidik od ivice do ivice ekrana i sklanjamo sve naslove trajno
    st.markdown("""
        <style>
            .main .block-container {
                max-width: 100% !important;
                padding-left: 0.5rem !important;
                padding-right: 0.5rem !important;
                padding-top: 1.5rem !important;
                padding-bottom: 0rem !important;
            }
            .stHeading, h1, h2, h3 {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

    fajl_csv = "POSADA_BAZA.csv"
    
    # Ako živa baza u fascikli još ne postoji, pravimo je iz Excela
    if not os.path.exists(fajl_csv) or os.path.getsize(fajl_csv) == 0:
        if os.path.exists(fajl_baze):
            try:
                df = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
                df.to_csv(fajl_csv, index=False)
            except:
                df = pd.DataFrame(columns=['SAP BROJ', 'PREZIME I IME', 'STATUS'])
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

    # --- POPRAVLJENO: UPIŠAN BROJ 2 ZA KOLONE SKROZ LEVO ---
    col_dugme, col_prazno = st.columns(2)
    
    with col_dugme:
        with st.popover("➕ DODAJ RADNIKA"):
            st.write("### Unesi novog radnika u sistem")
            novo_ime = st.text_input("Prezime i ime radnika:")
            novi_sap = st.text_input("SAP broj radnika:")
            if st.button("SAČUVAJ U POSADU"):
                if novo_ime:
                    novi_red = pd.DataFrame([{'SAP BROJ': novi_sap.strip(), 'PREZIME I IME': novo_ime.upper().strip(), 'STATUS': 'AKTIVAN'}])
                    df = pd.concat([df, novi_red], ignore_index=True)
                    df.to_csv(fajl_csv, index=False)
                    st.success("Radnik uspešno upisan!")
                    st.rerun()
                    
    st.write("")

    # Prikazujemo fiksiranu tabelu od ivice do ivice
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        key="zivi_editor_posade"
    )
    
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
