import streamlit as st
import pandas as pd
import os
from datetime import datetime
from nosioci import izracunaj_aktivnog_nosioca

def prikazi_raspored(fajl_baze):
    st.write("## 📅 Kalendarski raspored mehanizacije i vozača")
    
    fajl_csv = "raspored_baza.csv"
    danasnji_str = datetime.now().strftime('%d.%m.%Y')
    
    if not os.path.exists(fajl_csv) or os.path.getsize(fajl_csv) == 0:
        if os.path.exists(fajl_baze):
            df = pd.read_excel(fajl_baze, sheet_name='RASPORED')
            df = df.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
            df.columns = [col.strftime('%d.%m.%Y') if isinstance(col, datetime) else str(col) for col in df.columns]
            
            # Računamo inicijalno samo za brze potrebe
            for col in df.columns:
                if col not in ['MAŠINA', 'ID MAŠINE']:
                    nosioci_za_dan = izracunaj_aktivnog_nosioca(fajl_baze, col)
                    for idx, red in df.iterrows():
                        masina_id = str(red['ID MAŠINE']).strip()
                        if masina_id in nosioci_za_dan:
                            df.at[idx, col] = nosioci_za_dan[masina_id]
            df.to_csv(fajl_csv, index=False)
        else:
            st.error("Fajl 'plan.xlsm' nije pronađen.")
            return

    try:
        df = pd.read_csv(fajl_csv)
    except:
        return
        
    df = df.fillna('')
    
    st.write("### 📅 Filter kalendara")
    meseci = ["Januar", "Februar", "Mart", "April", "Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar", "Novembar", "Decembar"]
    trenutni_mesec_idx = datetime.now().month - 1
    izabrani_mesec = st.selectbox("Izaberi mesec za prikaz:", meseci, index=trenutni_mesec_idx, key="filter_meseca_rasp")
    
    mesec_broj_str = str(meseci.index(izabrani_mesec) + 1).zfill(2)
    ekstenzija_meseca = f".{mesec_broj_str}.2026"
    
    osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
    kalendarske_kolone = [c for c in df.columns if c.endswith(ekstenzija_meseca)]
    prikazane_kolone = osnovne_kolone + kalendarske_kolone

    opcije_radnika = [""]
    if os.path.exists('spisak_radnika.csv'):
        try:
            df_radnici_baza = pd.read_csv('spisak_radnika.csv')
            opcije_radnika.extend(sorted(df_radnici_baza['PREZIME I IME'].dropna().astype(str).unique()))
        except:
            pass

    konfiguracija_kolona = {
        "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True, disabled=True),
        "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True, disabled=True)
    }
    for col in kalendarske_kolone:
        naziv_zaglavlja = f"🚨 {col} (DANAS) 🚨" if col == danasnji_str else col
        konfiguracija_kolona[col] = st.column_config.SelectboxColumn(naziv_zaglavlja, options=opcije_radnika)

    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        column_order=prikazane_kolone,
        column_config=konfiguracija_kolona,
        key="editor_rasporeda_brzi"
    )
    
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
