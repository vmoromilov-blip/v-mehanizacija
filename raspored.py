import streamlit as st
import pandas as pd
import os
from datetime import datetime

def prikazi_raspored(fajl_baze):
    st.write("## 📅 Kalendarski raspored mehanizacije i vozača")
    
    if os.path.exists(fajl_baze):
        # 1. Čitamo originalni šit RASPORED iz Excela
        df = pd.read_excel(fajl_baze, sheet_name='RASPORED')
        df = df.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
        df.columns = [col.strftime('%d.%m.%Y') if isinstance(col, datetime) else str(col) for col in df.columns]
        
        # 2. 🚀 DOPUNA: Automatski lepimo KIPER-a i sve nove mašine sa plusića na dno tabele
        if os.path.exists('spisak_mašina.csv'):
            try:
                df_zive_masine = pd.read_csv('spisak_mašina.csv')
                for _, red in df_zive_masine.iterrows():
                    gb = str(red['GARAŽNI BROJ']).strip()
                    tip = str(red['TIP MAŠINE']).strip()
                    
                    # Proveravamo da li ta mašina već postoji na spisku
                    postojeci_gb = df['ID MAŠINE'].astype(str).str.strip().values
                    if gb not in postojeci_gb:
                        # Pravimo novi čist red za novu mašinu (sve ćelije u kalendaru ostaju prazne)
                        novi_red = {'MAŠINA': tip, 'ID MAŠINE': gb}
                        for col in df.columns:
                            if col not in ['MAŠINA', 'ID MAŠINE']:
                                novi_red[col] = ''
                        df = pd.concat([df, pd.DataFrame([novi_red])], ignore_index=True)
            except:
                pass
        
        danasnji_str = datetime.now().strftime('%d.%m.%Y')
        
        sve_kolone = list(df.columns)
        osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
        kalendarske_kolone = [c for c in sve_kolone if c not in osnovne_kolone]
        
        # 3. 🎯 AUTOMATSKO CENTRIRANJE NA DANAŠNJI DAN
        if danasnji_str in kalendarske_kolone:
            idx = kalendarske_kolone.index(danasnji_str)
            poredjane_kolone = osnovne_kolone + kalendarske_kolone[max(0, idx-2):] + kalendarske_kolone[:max(0, idx-2)]
        else:
            poredjane_kolone = sve_kolone

        konfiguracija_kolona = {
            "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True),
            "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True)
        }
        
        if danasnji_str in poredjane_kolone:
            konfiguracija_kolona[danasnji_str] = st.column_config.TextColumn(f"🚨 {danasnji_str} (DANAS) 🚨")

        # Prikazujemo brzu tabelu sa uključenim novim kiperom na dnu
        st.dataframe(
            df,
            use_container_width=True,
            column_order=poredjane_kolone,
            column_config=konfiguracija_kolona
        )
    else:
        st.error("Glavni Excel fajl 'plan.xlsm' nije pronađen u fascikli.")
