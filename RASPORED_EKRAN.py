import streamlit as st
import pandas as pd
import os
from datetime import datetime

# UVOZIMO TROSLOJNU MATEMATIKU U POZADINI (NOSIOCI + ISPRAVNOST + ZAMENA)
from RASPORED_MATEMATIKA import izracunaj_troslojni_raspored

def prikazi_raspored(fajl_baze):
    # CEMENTIRAMO MAKSIMALAN VIDIK OD IVICE DO IVICE EKRANA I SAKRIVAMO NASLOVE
    st.markdown("""
        <style>
            .main .block-container {
                max-width: 100% !important;
                padding-left: 0.5rem !important;
                padding-right: 0.5rem !important;
                padding-top: 1.5rem !important;
                padding-bottom: 0rem !important;
            }
            .stHeading, h1, h2, h3 {
                display: none !important;
            }
            .stDataEditor {
                width: 100% !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Pokrećemo moćni troslojni proračun u pozadini za samo 10 operativnih dana
    df, dani = izracunaj_troslojni_raspored(fajl_baze)
    
    if df.empty:
        st.error("Podaci za raspored nisu uspešno učitani iz baze.")
        return

    danasnji_str = datetime.now().strftime('%d.%m.%Y')
    osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
    
    # AUTOMATSKO CENTRIRANJE OKO DANAŠNJEG DANA UNUTAR OVIH 10 OPERATIVNIH DANA
    if danasnji_str in dani:
        idx_danas = dani.index(danasnji_str)
        poredjane_kolone = osnovne_kolone + dani[idx_danas-2:] + dani[:idx_danas-2]
    else:
        poredjane_kolone = osnovne_kolone + dani

    # Učitavamo spisak radnika iz vozača za brze padajuće menije unutar samih ćelija kalendara
    opcije_radnika = [""]
    if os.path.exists('POSADA_BAZA.csv'):
        try:
            df_radnici_baza = pd.read_csv('POSADA_BAZA.csv')
            if 'PREZIME I IME' in df_radnici_baza.columns:
                opcije_radnika.extend(sorted(df_radnici_baza['PREZIME I IME'].dropna().astype(str).unique()))
        except:
            pass

    # --- KONFIGURACIJA TABELE MEHANIZACIJE ---
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

    # Otvaramo miran, stabilan i maksimalno rastegnut data_editor bez ikakvih naslova
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        column_order=poredjane_kolone,
        column_config=konfiguracija_kolona,
        key="editor_troslojnog_rasporeda_finalni"
    )
    
    # Živi i trajni upis ako ručno promeniš ime vozača prstom na telefonu
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        fajl_csv = "raspored_baza.csv"
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
