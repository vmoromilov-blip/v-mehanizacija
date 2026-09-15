import streamlit as st
import pandas as pd
import os
from datetime import datetime

def prikazi_ispravnost(fajl_baze):
    st.write("## 🛠️ Dnevna ispravnost mehanizacije")
    
    fajl_csv = "ispravnost_baza.csv"
    
    # Ako fajl ne postoji, ili ako je pukao i ostao potpuno prazan
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
        df = pd.read_excel(fajl_baze, sheet_name='ISPRAVNOST')
        df = df.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
        df.columns = [col.strftime('%d.%m.%Y') if isinstance(col, datetime) else str(col) for col in df.columns]
        df.to_csv(fajl_csv, index=False)
        df = pd.read_csv(fajl_csv)
        
    df = df.fillna('DA')
    
    # --- AUTOMATSKO DODAVANJE NOVIH MAŠINA SA PLUSIĆA ---
    if os.path.exists('spisak_mašina.csv'):
        df_zive_masine = pd.read_csv('spisak_mašina.csv')
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
    # ----------------------------------------------------

    danasnji_str = datetime.now().strftime('%d.%m.%Y')
    
    # Čista forma za grupni prenos na više dana do kraja godine
    with st.popover("⚙️ Grupna promena (Prenos na više dana)"):
        st.write("### Unesi status i prenesi ga do kraja godine")
        izabrana_masina = st.selectbox("Izaberi mašinu (ID):", df['ID MAŠINE'].dropna().unique())
        datum_promene = st.date_input("Izaberi datum od kog prenosiš:", datetime.now().date())
        datum_promene_str = datum_promene.strftime('%d.%m.%Y')
        novi_status = st.radio("Status za prenos:", ["DA", "NE", "MIR", "VIK"], horizontal=True)
        
        if st.button("Sačuvaj i prenesi do kraja godine"):
            if datum_promene_str in df.columns:
                idx = df[df['ID MAŠINE'].astype(str).str.strip() == str(izabrana_masina).strip()].index
                if not idx.empty:
                    sve_kolone = list(df.columns)
                    start_idx = sve_kolone.index(datum_promene_str)
                    for c in sve_kolone[start_idx:]:
                        df.loc[idx, c] = novi_status
                    df.to_csv(fajl_csv, index=False)
                    st.success("Status uspešno prenet do kraja godine!")
                    st.rerun()
    st.write("")
    
    # --- VRAĆAMO SVE KOLONE OD 1. JANUARA ZA POTPUNU ISTORIJU ---
    prikazane_kolone = list(df.columns)

    # --- KONFIGURACIJA TABELE SA PADAJUĆIM MENIJIMA ---
    konfiguracija_kolona = {
        "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True, disabled=True),
        "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True, disabled=True)
    }
    
    for col in prikazane_kolone:
        if col not in ["MAŠINA", "ID MAŠINE"]:
            if col == danasnji_str:
                konfiguracija_kolona[col] = st.column_config.SelectboxColumn(
                    f"🚨 {col} (DANAS) 🚨",
                    options=["DA", "NE", "MIR", "VIK"],
                    required=True
                )
            else:
                konfiguracija_kolona[col] = st.column_config.SelectboxColumn(
                    col,
                    options=["DA", "NE", "MIR", "VIK"],
                    required=True
                )

    # Pokrećemo čisti data_editor sa celom istorijom i klizačem unazad
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        column_order=prikazane_kolone,
        column_config=konfiguracija_kolona,
        key="zivi_editor_ispravnosti"
    )
    
    # Živi i trajni upis iz padajućeg menija direktno u fasciklu
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
