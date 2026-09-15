import streamlit as st
import pandas as pd
import os
from datetime import datetime

def prikazi_raspored(fajl_baze):
    st.write("## 📅 Kalendarski raspored mehanizacije i vozača")
    
    if os.path.exists(fajl_baze):
        df = pd.read_excel(fajl_baze, sheet_name='RASPORED')
        df = df.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
        df.columns = [col.strftime('%d.%m.%Y') if isinstance(col, datetime) else str(col) for col in df.columns]
        
        fajl_zivih_masine = ""
        if os.path.exists('spisak_mašina.csv'):
            fajl_zivih_masine = 'spisak_mašina.csv'
        elif os.path.exists('spisak_masina.csv'):
            fajl_zivih_masine = 'spisak_masina.csv'
            
        if fajl_zivih_masine != "":
            try:
                df_zive_masine = pd.read_csv(fajl_zivih_masina)
                for _, red in df_zive_masine.iterrows():
                    gb = str(red['GARAŽNI BROJ']).strip()
                    tip = str(red['TIP MAŠINE']).strip()
                    postojeci_gb = df['ID MAŠINE'].astype(str).str.strip().values
                    if gb not in postojeci_gb:
                        novi_red = {'MAŠINA': tip, 'ID MAŠINE': gb}
                        for col in df.columns:
                            if col not in ['MAŠINA', 'ID MAŠINE']:
                                novi_red[col] = ''
                        df = pd.concat([df, pd.DataFrame([novi_red])], ignore_index=True)
            except:
                pass
        
        danasnji_str = datetime.now().strftime('%d.%m.%Y')
        trenutna_godina = datetime.now().strftime('%Y')
        
        st.write("### 📅 Filter kalendara")
        meseci = ["Januar", "Februar", "Mart", "April", "Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar", "Novembar", "Decembar"]
        trenutni_mesec_idx = datetime.now().month - 1
        izabrani_mesec = st.selectbox("Izaberi mesec za prikaz:", meseci, index=trenutni_mesec_idx, key="filter_mes_rasp_nov")
        
        mesec_broj_str = str(meseci.index(izabrani_mesec) + 1).zfill(2)
        ekstenzija_meseca = f".{mesec_broj_str}.{trenutna_godina}"
        
        sve_kolone = list(df.columns)
        osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
        kalendarske_kolone = [c for c in sve_kolone if c.endswith(ekstenzija_meseca)]
        
        if danasnji_str in kalendarske_kolone:
            idx = kalendarske_kolone.index(danasnji_str)
            poredjane_kolone = osnovne_kolone + kalendarske_kolone[max(0, idx-2):] + kalendarske_kolone[:max(0, idx-2)]
        else:
            poredjane_kolone = osnovne_kolone + kalendarske_kolone

        konfiguracija_kolona = {
            "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True),
            "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True)
        }
        if danasnji_str in poredjane_kolone:
            konfiguracija_kolona[danasnji_str] = st.column_config.TextColumn(f"🚨 {danasnji_str} (DANAS) 🚨")

        st.dataframe(
            df,
            use_container_width=True,
            column_order=poredjane_kolone,
            column_config=konfiguracija_kolona
        )
    else:
        st.error("Glavni Excel fajl 'plan.xlsm' nije pronađen.")
