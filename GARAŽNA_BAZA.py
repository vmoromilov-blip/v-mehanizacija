import streamlit as st
import pandas as pd
import os

def prikazi_garazu(fajl_baze):
    fajl_csv = "GARAZA_BAZA.csv"
    
    if not os.path.exists(fajl_csv) or os.path.getsize(fajl_csv) == 0:
        if os.path.exists(fajl_baze):
            try:
                df = pd.read_excel(fajl_baze, sheet_name='SPISAK MAŠINA')
                df.to_csv(fajl_csv, index=False)
            except:
                df = pd.DataFrame(columns=['TIP MAŠINE', 'GARAŽNI BROJ'])
        else:
            df = pd.DataFrame(columns=['TIP MAŠINE', 'GARAŽNI BROJ'])
            df.to_csv(fajl_csv, index=False)

    try:
        df = pd.read_csv(fajl_csv)
    except:
        return

    with st.popover("➕ DODAJ VOZILO"):
        st.write("### Unesi novo vozilo u sistem")
        novi_tip = st.text_input("Tip vozila (npr. KIPER, BAGER):")
        novi_gb = st.text_input("Garažni broj ili tablica:")
        if st.button("SAČUVAJ U GARAŽU"):
            if novi_tip and novi_gb:
                novi_red = pd.DataFrame([{'TIP MAŠINE': novi_tip.upper().strip(), 'GARAŽNI BROJ': novi_gb.upper().strip()}])
                df = pd.concat([df, novi_red], ignore_index=True)
                df.to_csv(fajl_csv, index=False)
                st.success("Vozilo trajno upisano!")
                st.rerun()
                    
    st.write("")

    # 🎯 TRAJNO CEMENTIRAMO PIN I ŠIRINU KOLONA ZA GARAŽU
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "TIP MAŠINE": st.column_config.TextColumn(
                "TIP MAŠINE", 
                pinned=True,     # OVO JE TRAJNI PIN!
                width="medium"   # KOMFORNA ŠIRINA DA SE SVE VIDI
            ),
            "GARAŽNI BROJ": st.column_config.TextColumn(
                "GARAŽNI BROJ", 
                width="medium"
            )
        },
        key="zivi_editor_garaze"
    )
    
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
