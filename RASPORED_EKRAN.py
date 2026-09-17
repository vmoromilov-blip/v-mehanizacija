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
    
    fajl_zivi_raspored = "raspored_zivi_unos.csv"
    danasnji_str = datetime.now().strftime('%d.%m.%Y')
    
    # Računamo osnovni troslojni raspored iz pozadinske matematike
    df_matematika, dani = izracunaj_troslojni_raspored(fajl_baze)
    
    if df_matematika.empty:
        st.error("Podaci za raspored nisu uspešno učitani iz baze.")
        return

    # Ako nemamo sačuvanu živu datoteku ručnih izmena, pravimo je na osnovu matematike
    if not os.path.exists(fajl_zivi_raspored) or os.path.getsize(fajl_zivi_raspored) == 0:
        df = df_matematika.copy()
        df.to_csv(fajl_zivi_raspored, index=False)
    else:
        try:
            df = pd.read_csv(fajl_zivi_raspored)
            df = df.fillna('')
            
            # Osiguravamo sinhronizaciju mašina iz baze mehanizacije
            df['ID MAŠINE'] = df['ID MAŠINE'].astype(str).str.strip().str.upper()
            df_matematika['ID MAŠINE'] = df_matematika['ID MAŠINE'].astype(str).str.strip().str.upper()
            
            for idx, red in df_matematika.iterrows():
                m_id = red['ID MAŠINE']
                if m_id not in df['ID MAŠINE'].values:
                    df = pd.concat([df, pd.DataFrame([red])], ignore_index=True)
        except:
            df = df_matematika.copy()

    osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
    
    # AUTOMATSKO CENTRIRANJE OKO DANAŠNJEG DANA UNUTAR OVIH 10 OPERATIVNIH DANA
    if danasnji_str in dani:
        idx_danas = dani.index(danasnji_str)
        poredjane_kolone = osnovne_kolone + dani[idx_danas-2:] + dani[:idx_danas-2]
    else:
        poredjane_kolone = osnovne_kolone + dani

    # Učitavamo spisak vozača za padajuće menije unutar ćelija kalendara
    opcije_radnika = [""]
    if os.path.exists('POSADA_BAZA.csv'):
        try:
            df_radnici_baza = pd.read_csv('POSADA_BAZA.csv')
            if 'PREZIME I IME' in df_radnici_baza.columns:
                opcije_radnika.extend(sorted(df_radnici_baza['PREZIME I IME'].dropna().astype(str).unique()))
        except:
            pass

    # --- KONFIGURACIJA TABELE: MAŠINE SU ZAKLJUČANE, A KALENDAR JE POTPUNO OTKLJUČAN ---
    konfiguracija_kolona = {
        "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True, disabled=True),
        "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True, disabled=True)
    }
    
    for col in dani:
        if col in df.columns:
            if len(opcije_radnika) > 1:
                konfiguracija_kolona[col] = st.column_config.SelectboxColumn(
                    f"🚨 {col} (DANAS) 🚨" if col == danasnji_str else col,
                    options=opcije_radnika,
                    required=False
                )
            else:
                konfiguracija_kolona[col] = st.column_config.TextColumn(f"🚨 {col} (DANAS) 🚨" if col == danasnji_str else col)

    # Otvaramo potpuno otključan živi data_editor od ivice do ivice ekrana
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        column_order=poredjane_kolone,
        column_config=konfiguracija_kolona,
        key="zivi_editor_troslojnog_rasporeda_otkljucani"
    )
    
    # 🎯 STOPRSTOTNO POPRAVLJEN I BEZBEDAN ŽIVI UPIS BEZ KOČENJA I MOTANJA
    if izmenjeni_df is not None:
        osnovni_df = pd.DataFrame(izmenjeni_df.values, columns=df.columns)
        if not osnovni_df.equals(df):
            osnovni_df.to_csv(fajl_zivi_raspored, index=False)
            st.rerun()
