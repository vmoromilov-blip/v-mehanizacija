import streamlit as st
import pandas as pd
import os
from datetime import datetime

# UVOZIMO NAŠE TRI NOVE SITNE POD-FIOKE ZA MAKSMALNO UBRZANJE
from raspored_baza import generisi_bazu_rasporeda
from raspored_filter import primeni_filter_ispravnosti
from raspored_zamena import primeni_vojne_zamene

def prikazi_raspored(fajl_baze):
    # 1. Pokrećemo prvi sloj: Računamo turnuse i nosioce za samo 10 operativnih dana
    df, dani = generisi_bazu_rasporeda(fajl_baze)
    
    # 2. Pokrećemo drugi sloj: Izbacujemo vozače sa mašina koje su u kvaru (NE, MIR, VIK)
    df = primeni_filter_ispravnosti(df, dani)
    
    # 3. Pokrećemo treći sloj: Primenjujemo izričite vojne naredbe iz Zamena
    df = primeni_vojne_zamene(df, dani)
    
    # Sva prazna polja čistimo da tabela izgleda uredno bez "NaN" reči
    df = df.fillna('')
    
    danasnji_str = datetime.now().strftime('%d.%m.%Y')
    osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
    
    # --- AUTOMATSKO CENTRIRANJE OKO DANAŠNJEG DANA UNUTAR OVIH 10 DANA ---
    if danasnji_str in dani:
        idx_danas = dani.index(danasnji_str)
        # Ekran skače tako da vidiš 2 dana unazad, DANAS, i 4 dana unapred (vikend i ponedeljak)
        poredjane_kolone = osnovne_kolone + dani[idx_danas-2:] + dani[:idx_danas-2]
    else:
        poredjane_kolone = osnovne_kolone + dani

    # Učitavamo spisak radnika za brze padajuće menije u ćelijama na telefonu
    opcije_radnika = [""]
    if os.path.exists('spisak_radnika.csv'):
        try:
            df_radnici_baza = pd.read_csv('spisak_radnika.csv')
            if 'PREZIME I IME' in df_radnici_baza.columns:
                opcije_radnika.extend(sorted(df_radnici_baza['PREZIME I IME'].dropna().astype(str).unique()))
        except:
            pass

    # --- KONFIGURACIJA TABELE SA PADAJUĆIM MENIJIMA RADNIKA ---
    konfiguracija_kolona = {
        "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True, disabled=True),
        "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True, disabled=True)
    }
    
    for col in dani:
        if len(opcije_radnika) > 1:
            konfiguracija_kolona[col] = st.column_config.SelectboxColumn(
                f"🚨 {col} (DANAS) 🚨" if col == danasnji_str else col,
                options=opcije_radnika
            )
        else:
            konfiguracija_kolona[col] = st.column_config.TextColumn(f"🚨 {col} (DANAS) 🚨" if col == danasnji_str else col)

    # Pokrećemo brzi data_editor sa prozorom od 10 operativnih dana
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        column_order=poredjane_kolone,
        column_config=konfiguracija_kolona,
        key="zivi_editor_rasporeda_10dana"
    )
    
    # Živi i trajni upis ako ručno promeniš ime vozača prstom na telefonu
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        fajl_csv = "raspored_baza.csv"
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
