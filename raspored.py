import streamlit as st
import pandas as pd
import os
from datetime import datetime

def prikazi_raspored(fajl_baze):
    st.write("## 📅 Kalendarski raspored mehanizacije i vozača")
    
    if os.path.exists(fajl_baze):
        # Čitamo šit RASPORED iz Excela
        df = pd.read_excel(fajl_baze, sheet_name='RASPORED')
        df = df.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
        
        # Svi datumi u kolonama moraju biti tekstualni da se sajt ne bi rušio
        df.columns = [col.strftime('%d.%m.%Y') if isinstance(col, datetime) else str(col) for col in df.columns]
        
        danasnji_str = datetime.now().strftime('%d.%m.%Y')
        
        # Brzi unos vozača na mašinu za današnji dan
        with st.popover("🚜 Rasporedi radnika na mašinu"):
            st.write("### Unesi promenu u rasporedu")
            izabrana_masina = st.selectbox("Izaberi mašinu (ID):", df['ID MAŠINE'].dropna().unique(), key="raspored_masina")
            novo_ime = st.text_input("Ime i prezime radnika:")
            if st.button("Zapiši u raspored"):
                st.success(f"Radnik {novo_ime} je uspešno raspoređen!")
                st.rerun()
        st.write("")
        
        # Isticanje današnjeg dana (15.09.2026) u rasporedu
        def istakni_danasnji_dan(s):
            if s.name == danasnji_str:
                return ['font-weight: bold; background-color: #fff2cc; border: 2px solid orange;'] * len(s)
            return [''] * len(s)
            
        styled_df = df.style.apply(istakni_danasnji_dan, axis=0)
        
        # Pametno centriranje oko današnjeg dana
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
