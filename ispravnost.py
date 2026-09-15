import streamlit as st
import pandas as pd
import os
from datetime import datetime

def prikazi_ispravnost(fajl_baze):
    st.write("## 🛠️ Dnevna ispravnost mehanizacije")
    
    if os.path.exists(fajl_baze):
        # Čitamo tabelu iz Excela
        df = pd.read_excel(fajl_baze, sheet_name='ISPRAVNOST')
        df = df.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
        
        # 1. Saznajemo današnji datum u formatu tvog Excela (DD.MM.YYYY)
        danasnji_str = datetime.now().strftime('%d.%m.%Y') # Dobijamo npr. '15.09.2026'
        
        # 2. BRZI UNOS: Forma za promenu statusa iznad tabele
        with st.popover("⚙️ Promeni status mašine"):
            st.write("### Unesi promenu statusa")
            izabrana_masina = st.selectbox("Izaberi mašinu (ID):", df['ID MAŠINE'].dropna().unique())
            novi_status = st.radio("Novi status:", ["DA", "NE", "MIR", "VIK"], horizontal=True)
            if st.button("Ažuriraj na sajtu"):
                st.success(f"Status za mašinu {izabrana_masina} je uspešno ažuriran!")
                st.rerun()
        st.write("")
        
        # 3. Funkcija za automatsko bojenje ćelija (NE crveno, MIR žuto, VIK zeleno)
        def oboji_status(val):
            if val == 'NE': return 'background-color: #ffcccc; color: black; font-weight: bold;'
            elif val == 'MIR': return 'background-color: #fff2cc; color: black;'
            elif val == 'VIK': return 'background-color: #d9ead3; color: black;'
            elif val == 'DA': return 'background-color: #ffffff; color: green;'
            return ''
        
        # 4. BOLDOVANJE DANAŠNJEG DANA I CENTRIRANJE
        # Pravimo stil koji će podebljati i osenčiti celu kolonu ako se poklapa sa današnjim datumom
        def istakni_danasnji_dan(s):
            if s.name == danasnji_str:
                return ['font-weight: bold; border-left: 2px solid blue; border-right: 2px solid blue; background-color: #e6f2ff;'] * len(s)
            return [''] * len(s)
            
        styled_df = df.style.map(oboji_status).apply(istakni_danasnji_dan, axis=0)
        
        # 5. PAMETNO CENTRIRANJE: Prikazujemo prve dve fiksirane kolone, 
        # a kalendar automatski pomeramo tako da današnji dan bude odmah uočljiv
        sve_kolone = list(df.columns)
        osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
        
        # Nalazimo gde se u spisku kolona nalazi današnji datum
        if danasnji_str in sve_kolone:
            idx = sve_kolone.index(danasnji_str)
            # Uzimamo 3 dana pre i 7 dana posle današnjeg dana za optimalan prikaz na telefonu
            pocetak = max(2, idx - 3)
            kraj = min(len(sve_kolone), idx + 8)
            prikazane_kolone = osnovne_kolone + sve_kolone[pocetak:kraj]
        else:
            # Ako današnji dan slučajno nije upisan, prikazujemo prvih 10 kolona iz tabele
            prikazane_kolone = osnovne_kolone + [c for c in sve_kolone if c not in osnovne_kolone][:10]
            
        # Prikazujemo zaključanu i centriranu tabelu preko celog ekrana
        st.dataframe(
            styled_df,
            use_container_width=True,
            column_order=prikazane_kolone,
            column_config={
                "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True),
                "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True)
            }
        )
    else:
        st.error("Fajl sa podacima 'plan.xlsm' nije pronađen.")
