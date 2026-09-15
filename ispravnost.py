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
        
        # 1. Funkcija za automatsko bojenje ćelija
        def oboji_status(val):
            if val == 'NE': return 'background-color: #ffcccc; color: black; font-weight: bold;'
            elif val == 'MIR': return 'background-color: #fff2cc; color: black;'
            elif val == 'VIK': return 'background-color: #d9ead3; color: black;'
            elif val == 'DA': return 'background-color: #ffffff; color: green;'
            return ''
        
        # 2. Isticanje današnjeg dana
        def istakni_danasnji_dan(s):
            if s.name == danasnji_str:
                return ['font-weight: bold; background-color: #e6f2ff; border: 2px solid blue;'] * len(s)
            return [''] * len(s)
            
        styled_df = df.style.map(oboji_status).apply(istakni_danasnji_dan, axis=0)
        
        # 3. Pametno centriranje kolona oko današnjeg dana
        sve_kolone = list(df.columns)
        osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
        
        if danasnji_str in sve_kolone:
            idx = sve_kolone.index(danasnji_str)
            pocetak = max(2, idx - 2)
            kraj = min(len(sve_kolone), idx + 6)
            prikazane_kolone = osnovne_kolone + sve_kolone[pocetak:kraj]
        else:
            prikazane_kolone = osnovne_kolone + [c for c in sve_kolone if c not in osnovne_kolone][:8]
            
        # --- NOVI SISTEM: DIREKTNO MENJANJE U ĆELIJAMA ---
        # Koristimo st.data_editor umesto st.dataframe i hvatamo sve izmene u hodu
        izmenjena_tabela = st.data_editor(
            styled_df,
            use_container_width=True,
            column_order=prikazane_kolone,
            column_config={
                "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True, disabled=True),
                "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True, disabled=True)
            },
            key="kalendar_ispravnosti"
        )
        
        # Ako je korisnik promenio bilo koje slovo direktno u tabeli, sajt to odmah trajno čuva
        if izmenjena_tabela is not None and not izmenjena_tabela.equals(df):
            izmenjena_tabela.to_csv(fajl_csv, index=False)
            st.success("Izmene u kalendaru su uspešno sačuvane!")
            st.rerun()
            
    else:
        st.error("Baza podataka nije dostupna.")
