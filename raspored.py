import streamlit as st
import pandas as pd
import os
from datetime import datetime

def prikazi_raspored(fajl_baze):
    st.write("## 📅 Kalendarski raspored mehanizacije i vozača")
    
    if os.path.exists(fajl_baze):
        # Čitamo originalni šit RASPORED direktno iz tvog Excela
        df = pd.read_excel(fajl_baze, sheet_name='RASPORED')
        df = df.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
        
        # Sredjujemo datume u kolonama da budu čitljivi
        df.columns = [col.strftime('%d.%m.%Y') if isinstance(col, datetime) else str(col) for col in df.columns]
        
        danasnji_str = datetime.now().strftime('%d.%m.%Y')
        
        sve_kolone = list(df.columns)
        osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
        kalendarske_kolone = [c for c in sve_kolone if c not in osnovne_kolone]
        
        # --- AUTOMATSKO CENTRIRANJE EKRAZA NA DANAŠNJI DAN ---
        if danasnji_str in kalendarske_kolone:
            idx = kalendarske_kolone.index(danasnji_str)
            # Prikazujemo 2 dana pre danas, i sve dane unapred do kraja godine, sa punim klizačem
            poredjane_kolone = osnovne_kolone + kalendarske_kolone[max(0, idx-2):] + kalendarske_kolone[:max(0, idx-2)]
        else:
            poredjane_kolone = sve_kolone

        konfiguracija_kolona = {
            "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True),
            "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True)
        }
        
        if danasnji_str in poredjane_kolone:
            konfiguracija_kolona[danasnji_str] = st.column_config.TextColumn(f"🚨 {danasnji_str} (DANAS) 🚨")

        # Prikazujemo čistu i brzu tabelu direktno iz tvog Excela
        st.dataframe(
            df,
            use_container_width=True,
            column_order=poredjane_kolone,
            column_config=konfiguracija_kolona
        )
    else:
        st.error("Glavni Excel fajl 'plan.xlsm' nije pronađen u fascikli.")
