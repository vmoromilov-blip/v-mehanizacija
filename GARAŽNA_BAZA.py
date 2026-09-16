import streamlit st as st
import pandas as pd
import os

def prikazi_garazu(fajl_baze):
    # Fiksiramo pogled: Tabela ide od ivice do ivice ekrana, a dugme spuštamo malo nadole da ga ekran ne seče
    st.markdown("""
        <style>
            .main .block-container {
                max-width: 100% !important;
                padding-left: 0.5rem !important;
                padding-right: 0.5rem !important;
                padding-top: 1.5rem !important; /* Spušteno sa 0 na 1.5 da dugme izađe iz oblaka */
                padding-bottom: 0rem !important;
            }
            .stHeading, h1, h2, h3 {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

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

    # Dugmad lepa i skraćena skroz na levoj strani
    col_dugme, col_prazno = st.columns(2)
    
    with col_dugme:
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

    # Tabela zacementirana od ivice do ivice
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        key="zivi_editor_garaze"
    )
    
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
