import streamlit as st
import pandas as pd
import os
from datetime import datetime

def prikazi_ispravnost(fajl_baze):
    st.write("## 🛠️ Dnevna ispravnost mehanizacije")
    
    fajl_csv = "ispravnost_baza.csv"
    
    if not os.path.exists(fajl_csv) and os.path.exists(fajl_baze):
        df = pd.read_excel(fajl_baze, sheet_name='ISPRAVNOST')
        df = df.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
        df.columns = [col.strftime('%d.%m.%Y') if isinstance(col, datetime) else str(col) for col in df.columns]
        df.to_csv(fajl_csv, index=False)
    
    if os.path.exists(fajl_csv):
        df = pd.read_csv(fajl_csv)
        
        # Svi prazni dani (None/NaN) se automatski popunjavaju sa "DA" da ne kvare tabelu
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
        
        # --- ŽIVI UNOS: PROZORČIĆ KOJI PRENOSI STANJE NA NAREDNE DANE ---
        with st.popover("⚙️ Promeni status mašine"):
            st.write("### Unesi promenu statusa u kalendar")
            izabrana_masina = st.selectbox("Izaberi mašinu (ID):", df['ID MAŠINE'].dropna().unique())
            datum_promene = st.date_input("Izaberi datum za izmenu:", datetime.now().date())
            datum_promene_str = datum_promene.strftime('%d.%m.%Y')
            novi_status = st.radio("Novi status:", ["DA", "NE", "MIR", "VIK"], horizontal=True)
            prenesi_dalje = st.checkbox("Prenesi ovaj status na sve naredne dane u godini", value=True)
            
            if st.button("Sačuvaj promenu trajno"):
                if datum_promene_str in df.columns:
                    idx = df[df['ID MAŠINE'].astype(str).str.strip() == str(izabrana_masina).strip()].index
                    if not idx.empty:
                        if prenesi_dalje:
                            sve_kolone = list(df.columns)
                            start_idx = sve_kolone.index(datum_promene_str)
                            for c in sve_kolone[start_idx:]:
                                df.loc[idx, c] = novi_status
                        else:
                            df.loc[idx, datum_promene_str] = novi_status
                        
                        df.to_csv(fajl_csv, index=False)
                        st.success(f"Status trajno zabeležen u fascikli kalendara!")
                        st.rerun()
                else:
                    st.error(f"Izabrani datum {datum_promene_str} se ne nalazi u kalendaru.")
        st.write("")
        
        # Funkcija za boje
        def oboji_status(val):
            if val == 'NE': return 'background-color: #ffcccc; color: black; font-weight: bold;'
            elif val == 'MIR': return 'background-color: #fff2cc; color: black;'
            elif val == 'VIK': return 'background-color: #d9ead3; color: black;'
            elif val == 'DA': return 'background-color: #ffffff; color: green; font-weight: bold;'
            return ''
        
        # Funkcija za boldovanje današnjeg dana
        def istakni_danasnji_dan(s):
            if s.name == danasnji_str:
                return ['font-weight: bold; background-color: #e6f2ff; border: 2px solid blue; color: black;'] * len(s)
            return [''] * len(s)
            
        styled_df = df.style.map(oboji_status).apply(istakni_danasnji_dan, axis=0)
        
        sve_kolone = list(df.columns)
        osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
        
        if danasnji_str in sve_kolone:
            idx = sve_kolone.index(danasnji_str)
            pocetak = max(2, idx - 2)
            kraj = min(len(sve_kolone), idx + 6)
            prikazane_kolone = osnovne_kolone + sve_kolone[pocetak:kraj]
        else:
            prikazane_kolone = osnovne_kolone + [c for c in sve_kolone if c not in osnovne_kolone][:8]
            
        # Vraćamo st.dataframe format koji podržava napredne stilove i boje
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
        st.error("Baza podataka nije dostupna.")
