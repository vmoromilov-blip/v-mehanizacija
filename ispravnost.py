import streamlit as st
import pandas as pd
import os
from datetime import datetime

def prikazi_ispravnost(fajl_baze):
    st.write("## 🛠️ Dnevna ispravnost mehanizacije")
    
    if os.path.exists(fajl_baze):
        df = pd.read_excel(fajl_baze, sheet_name='ISPRAVNOST')
        df = df.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
        
        # Svi datumi u kolonama moraju biti tekstualni da se sajt ne bi rušio
        df.columns = [col.strftime('%d.%m.%Y') if isinstance(col, datetime) else str(col) for col in df.columns]
        
        danasnji_str = datetime.now().strftime('%d.%m.%Y')
        
        with st.popover("⚙️ Promeni status mašine"):
            st.write("### Unesi promenu statusa")
            izabrana_masina = st.selectbox("Izaberi mašinu (ID):", df['ID MAŠINE'].dropna().unique())
            novi_status = st.radio("Novi status:", ["DA", "NE", "MIR", "VIK"], horizontal=True)
            if st.button("Ažuriraj na sajtu"):
                st.success(f"Status za mašinu {izabrana_masina} je uspešno ažuriran!")
                st.rerun()
        st.write("")
        
        def oboji_status(val):
            if val == 'NE': return 'background-color: #ffcccc; color: black; font-weight: bold;'
            elif val == 'MIR': return 'background-color: #fff2cc; color: black;'
            elif val == 'VIK': return 'background-color: #d9ead3; color: black;'
            elif val == 'DA': return 'background-color: #ffffff; color: green;'
            return ''
        
        def istakni_danasnji_dan(s):
            if s.name == danasnji_str:
                return ['font-weight: bold; background-color: #e6f2ff; border: 2px solid blue;'] * len(s)
            return [''] * len(s)
            
        styled_df = df.style.map(oboji_status).apply(istakni_danasnji_dan, axis=0)
        
        # Pametno centriranje kolona oko današnjeg dana
        sve_kolone = list(df.columns)
        osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
        
        if danasnji_str in sve_kolone:
            idx = sve_kolone.index(danasnji_str)
            pocetak = max(2, idx - 2)
            kraj = min(len(sve_kolone), idx + 6)
            prikazane_kolone = osnovne_kolone + sve_kolone[pocetak:kraj]
        else:
            prikazane_kolone = osnovne_kolone + [c for c in sve_kolone if c not in osnovne_kolone][:8]
            
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
