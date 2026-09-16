import streamlit as st
import pandas as pd
import os

def prikazi_posadu(fajl_baze):
    fajl_csv = "POSADA_BAZA.csv"
    
    # Ako fajl u memoriji ne postoji, pravimo ga iz Excela
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

    # --- 🧼 HIRURŠKO ČIŠĆENJE VIŠKOVA I UPISIVANJE REČI "AKTIVAN" ---
    # 1. Prisno izbacujemo neželjene kolone iz prikaza
    kolone_za_izbacivanje = ['EMAIL ADRESA', 'TIP', 'Unnamed: 3']
    df = df.drop(columns=[c for c in kolone_za_izbacivanje if c in df.columns], errors='ignore')
    
    # 2. Ako kolona STATUS postoji, punimo je rečju AKTIVAN, ako ne postoji - pravimo je!
    df['STATUS'] = 'AKTIVAN'
    # -----------------------------------------------------------------

    # Čisto dugme na samom vrhu ekrana
    with st.popover("➕ DODAJ RADNIKA"):
        st.write("### Unesi novog radnika u sistem")
        novo_ime = st.text_input("Prezime i ime radnika:")
        novi_sap = st.text_input("SAP broj radnika:")
        if st.button("SAČUVAJ U VOZAČE"):
            if novo_ime:
                novi_red = pd.DataFrame([{
                    'SAP BROJ': novi_sap.strip(), 
                    'PREZIME I IME': novo_ime.upper().strip(), 
                    'STATUS': 'AKTIVAN'
                }])
                df = pd.concat([df, novi_red], ignore_index=True)
                df.to_csv(fajl_csv, index=False)
                st.success("Radnik uspešno upisan!")
                st.rerun()
                    
    st.write("")

    # Čista i brza tabela bez ikakvih rizičnih parametara koji ruše sajt
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        key="zivi_editor_radnika_cist_i_siguran"
    )
    
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
