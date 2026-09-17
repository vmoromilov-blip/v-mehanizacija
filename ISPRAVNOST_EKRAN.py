import streamlit as st
import pandas as pd
import os
from datetime import datetime

# UVOZIMO POZADINSKU MATEMATIKU DA NAM TABELA NE BI TREPTALA
from ISPRAVNOST_MATEMATIKA import (
    inicijalizuj_bazu_ispravnosti, 
    dodaj_nova_vozila_u_ispravnost, 
    izvrsi_projektovanje_ispravnosti
)

def prikazi_ispravnost(fajl_baze):
    # CEMENTIRAMO MAKSIMALAN VIDIK OD IVICE DO IVICE EKRANA I BRIŠEMO NASLOVE
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
            .stDataEditor {
                width: 100% !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    fajl_csv = "ispravnost_baza.csv"
    trenutna_godina = datetime.now().strftime('%Y')
    danasnji_str = datetime.now().strftime('%d.%m.%Y')
    
    # Pokrećemo pozadinsko čitanje (Excel se čita samo ako CSV ne postoji!)
    inicijalizuj_bazu_ispravnosti(fajl_baze, fajl_csv)

    try:
        df = pd.read_csv(fajl_csv)
    except:
        return
        
    df = df.fillna('DA')
    
    # Automatski lepimo nova vozila sa plusića na dno (kiper VM)
    df = dodaj_nova_vozila_u_ispravnost(df, fajl_csv)

    # 🎯 AUTOMATSKO SORTIRANJE CELOG KALENDARA OD A DO Z PO GARAŽNOM BROJU
    if 'ID MAŠINE' in df.columns:
        df = df.sort_values(by='ID MAŠINE').reset_index(drop=True)

    # --- DUGMAD NA KRILIMA: ISPRAVNOST LEVO, IZBOR MESECA DESNO ---
    col_dugme, col_razmak, col_mesec = st.columns([1, 2, 1])
    
    with col_dugme:
        with st.popover("⚙️ ISPRAVNOST"):
            st.write("### Projektuj ispravnost do kraja godine")
            p_masina = st.selectbox("Izaberi mašinu (ID):", df['ID MAŠINE'].dropna().unique(), key="proj_mas")
            p_datum = st.date_input("Od datuma:", datetime.now().date(), key="proj_dat")
            p_status = st.radio("Status za prenos:", ["DA", "NE", "MIR", "VIK"], horizontal=True, key="proj_stat")
            
            if st.button("Zapiši i projektuj trajno", key="proj_btn"):
                p_datum_str = p_datum.strftime('%d.%m.%Y')
                uspeh = izvrsi_projektovanje_ispravnosti(df, p_masina, p_datum_str, p_status, fajl_csv)
                if uspeh:
                    st.success("Uspešno projektovano do kraja godine!")
                    st.rerun()
                else:
                    st.error(f"Izabrani datum {p_datum_str} se ne nalazi u kalendaru.")

    with col_mesec:
        meseci = ["Januar", "Februar", "Mart", "April", "Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar", "Novembar", "Decembar"]
        trenutni_mesec_idx = datetime.now().month - 1
        izabrani_mesec = st.selectbox("Izaberi mesec:", meseci, index=trenutni_mesec_idx, label_visibility="collapsed")

    st.write("")
    
    mesec_broj_str = str(meseci.index(izabrani_mesec) + 1).zfill(2)
    ekstenzija_meseca = f".{mesec_broj_str}.{trenutna_godina}"
    
    osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
    kalendarske_kolone = [c for c in df.columns if c.endswith(ekstenzija_meseca)]
    
    # Automatski skakač na današnji dan unutar tekućeg meseca
    if danasnji_str in kalendarske_kolone:
        idx_danas = kalendarske_kolone.index(danasnji_str)
        poredjane_kolone = osnovne_kolone + kalendarske_kolone[max(0, idx_danas-2):] + kalendarske_kolone[:max(0, idx_danas-2)]
    else:
        poredjane_kolone = osnovne_kolone + kalendarske_kolone

    # Konfigurišemo brze padajuće menije unutar samih ćelija kalendara
    konfiguracija_kolona = {
        "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True, disabled=True),
        "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True, disabled=True)
    }
    for col in kalendarske_kolone:
        naziv_zaglavlja = f"🚨 {col} (DANAS) 🚨" if col == danasnji_str else col
        konfiguracija_kolona[col] = st.column_config.SelectboxColumn(naziv_zaglavlja, options=["DA", "NE", "MIR", "VIK"], required=True)

    # Otvaramo miran, stabilan i maksimalno rastegnut data_editor
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        column_order=poredjane_kolone,
        column_config=konfiguracija_kolona,
        key="editor_ispravnosti_brzi_finalni"
    )
    
    if izmenjeni_df is not None:
        osnovni_df = pd.DataFrame(izmenjeni_df.values, columns=df.columns)
        if not osnovni_df.equals(df):
            osnovni_df.to_csv(fajl_csv, index=False)
            st.rerun()
