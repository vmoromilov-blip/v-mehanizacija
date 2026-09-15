import streamlit as st
import pandas as pd
import os
from datetime import datetime

def prikazi_ispravnost(fajl_baze):
    st.write("## 🛠️ Dnevna ispravnost mehanizacije")
    
    fajl_csv = "ispravnost_baza.csv"
    
    if not os.path.exists(fajl_csv) or os.path.getsize(fajl_csv) == 0:
        if os.path.exists(fajl_baze):
            df = pd.read_excel(fajl_baze, sheet_name='ISPRAVNOST')
            df = df.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
            df.columns = [col.strftime('%d.%m.%Y') if isinstance(col, datetime) else str(col) for col in df.columns]
            df.to_csv(fajl_csv, index=False)
        else:
            st.error("Fajl 'plan.xlsm' nije pronađen.")
            return

    try:
        df = pd.read_csv(fajl_csv)
    except:
        return
        
    df = df.fillna('DA')
    danasnji_str = datetime.now().strftime('%d.%m.%Y')
    
    # --- PADAJUĆI MENI ZA IZBOR MESECA (UBRZANJE!) ---
    st.write("### 📅 Filter kalendara")
    meseci = ["Januar", "Februar", "Mart", "April", "Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar", "Novembar", "Decembar"]
    trenutni_mesec_idx = datetime.now().month - 1
    izabrani_mesec = st.selectbox("Izaberi mesec za prikaz:", meseci, index=trenutni_mesec_idx)
    
    mesec_broj_str = str(meseci.index(izabrani_mesec) + 1).zfill(2)
    ekstenzija_meseca = f".{mesec_broj_str}.2026"
    
    osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
    kalendarske_kolone = [c for c in df.columns if c.endswith(ekstenzija_meseca)]
    prikazane_kolone = osnovne_kolone + kalendarske_kolone

    # --- PADAJUĆI MENIJI U ĆELIJAMA ---
    konfiguracija_kolona = {
        "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True, disabled=True),
        "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True, disabled=True)
    }
    for col in kalendarske_kolone:
        naziv_zaglavlja = f"🚨 {col} (DANAS) 🚨" if col == danasnji_str else col
        konfiguracija_kolona[col] = st.column_config.SelectboxColumn(naziv_zaglavlja, options=["DA", "NE", "MIR", "VIK"], required=True)

    # --- VRATILI SMO SVE BOJE! ---
    def oboji_status(val):
        if val == 'NE': return 'background-color: #ffcccc; color: black; font-weight: bold;'
        elif val == 'MIR': return 'background-color: #fff2cc; color: black;'
        elif val == 'VIK': return 'background-color: #d9ead3; color: black;'
        elif val == 'DA': return 'background-color: #ffffff; color: green; font-weight: bold;'
        return ''
        
    styled_df = df.style.map(oboji_status)

    izmenjeni_df = st.data_editor(
        styled_df,
        use_container_width=True,
        column_order=prikazane_kolone,
        column_config=konfiguracija_kolona,
        key="editor_ispravnosti_brzi"
    )
    
    if izmenjeni_df is not None:
        # Čuvamo promenu u pozadini
        osnovni_df = pd.DataFrame(izmenjeni_df.values, columns=df.columns)
        if not osnovni_df.equals(df):
            osnovni_df.to_csv(fajl_csv, index=False)
            st.rerun()
