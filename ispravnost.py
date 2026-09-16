import streamlit as st
import pandas as pd
import os
from datetime import datetime

def prikazi_ispravnost(fajl_baze):
    # 🎯 BRUTALNO CEMENTIRANJE VIDIKA: Širimo sajt na 100% širine od ivice do ivice ekrana i brišemo sve naslove trajno
    st.markdown("""
        <style>
            /* Širenje glavnog kontejnera na 100% širine ekrana */
            .main .block-container {
                max-width: 100% !important;
                padding-left: 0.5rem !important;
                padding-right: 0.5rem !important;
                padding-top: 0rem !important;
                padding-bottom: 0rem !important;
            }
            /* Sakrivanje svih fabričkih naslova i viškova prostora */
            .stHeading, h1, h2, h3 {
                display: none !important;
            }
            /* Dodatno stezanje praznog prostora iznad tabele */
            div.block-container {
                padding-top: 0.5rem !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    fajl_csv = "ispravnost_baza.csv"
    trenutna_godina = datetime.now().strftime('%Y')
    danasnji_str = datetime.now().strftime('%d.%m.%Y')
    
    if not os.path.exists(fajl_csv) or os.path.getsize(fajl_csv) == 0:
        if os.path.exists(fajl_baze):
            df = pd.read_excel(fajl_baze, sheet_name='ISPRAVNOST')
            df = df.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
            df.columns = [col.strftime('%d.%m.%Y') if isinstance(col, datetime) else str(col) for col in df.columns]
            df.to_csv(fajl_csv, index=False)
        else:
            st.error("Glavni Excel fajl 'plan.xlsm' nije pronađen.")
            return

    try:
        df = pd.read_csv(fajl_csv)
    except:
        return
        
    df = df.fillna('DA')
    
    # --- AUTOMATSKO DODAVANJE NOVIH MAŠINA SA PLUSIĆA ---
    fajl_zivih = 'spisak_mašina.csv' if os.path.exists('spisak_mašina.csv') else ('spisak_masina.csv' if os.path.exists('spisak_masina.csv') else '')
    if fajl_zivih != "":
        try:
            df_zive_masine = pd.read_csv(fajl_zivih)
            for _, red in df_zive_masine.iterrows():
                gb = str(red['GARAŽNI BROJ']).strip()
                tip = str(red['TIP MAŠINE']).strip()
                
                postojeci_gb = df['ID MAŠINE'].astype(str).str.strip().values
                if gb not in postojeci_gb:
                    novi_red = {'MAŠINA': tip, 'ID MAŠINE': gb}
                    for col in df.columns:
                        if col not in ['MAŠINA', 'ID MAŠINE']:
                            novi_red[col] = 'DA'
                    df = pd.concat([df, pd.DataFrame([novi_red])], ignore_index=True)
            df.to_csv(fajl_csv, index=False)
        except:
            pass

    # --- LEPŠA I KORPAKTNIJA DUGMAD U ISTOJ LINIJI ---
    col_izbor, col_projektuj = st.columns([1, 2])
    
    with col_izbor:
        meseci = ["Januar", "Februar", "Mart", "April", "Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar", "Novembar", "Decembar"]
        trenutni_mesec_idx = datetime.now().month - 1
        izabrani_mesec = st.selectbox("Mesec:", meseci, index=trenutni_mesec_idx, label_visibility="collapsed")
    
    with col_projektuj:
        with st.popover("⚙️ Projektuj ispravnost do kraja godine"):
            st.write("### Unesi status i prenesi ga automatski na sve naredne dane")
            p_masina = st.selectbox("Izaberi mašinu (ID):", df['ID MAŠINE'].dropna().unique(), key="proj_mas")
            p_datum = st.date_input("Od datuma:", datetime.now().date(), key="proj_dat")
            p_status = st.radio("Status:", ["DA", "NE", "MIR", "VIK"], horizontal=True, key="proj_stat")
            
            if st.button("Zapiši i projektuj trajno", key="proj_btn"):
                p_datum_str = p_datum.strftime('%d.%m.%Y')
                if p_datum_str in df.columns:
                    idx = df[df['ID MAŠINE'].astype(str).str.strip() == str(p_masina).strip()].index
                    if not idx.empty:
                        sve_kolone = list(df.columns)
                        start_idx = sve_kolone.index(p_datum_str)
                        for c in sve_kolone[start_idx:]:
                            df.loc[idx, c] = p_status
                        df.to_csv(fajl_csv, index=False)
                        st.success("Uspešno projektovano!")
                        st.rerun()
    
    mesec_broj_str = str(meseci.index(izabrani_mesec) + 1).zfill(2)
    ekstenzija_meseca = f".{mesec_broj_str}.{trenutna_godina}"
    
    osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
    kalendarske_kolone = [c for c in df.columns if c.endswith(ekstenzija_meseca)]
    
    if danasnji_str in kalendarske_kolone:
        idx_danas = kalendarske_kolone.index(danasnji_str)
        poredjane_kolone = osnovne_kolone + kalendarske_kolone[max(0, idx_danas-2):] + kalendarske_kolone[:max(0, idx_danas-2)]
    else:
        poredjane_kolone = osnovne_kolone + kalendarske_kolone

    konfiguracija_kolona = {
        "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True, disabled=True),
        "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True, disabled=True)
    }
    for col in kalendarske_kolone:
        naziv_zaglavlja = f"🚨 {col} (DANAS) 🚨" if col == danasnji_str else col
        konfiguracija_kolona[col] = st.column_config.SelectboxColumn(naziv_zaglavlja, options=["DA", "NE", "MIR", "VIK"], required=True)

    # Pokrećemo fiksiranu, maksimalno široku tabelu uz samu gornju ivicu ekrana
    st.data_editor(
        df,
        use_container_width=True,
        column_order=poredjane_kolone,
        column_config=konfiguracija_kolona,
        key="editor_ispravnosti_brzi"
    )
