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
    
    fajl_rucnih_promena = "raspored_rucne_promene.csv"
    danasnji_str = datetime.now().strftime('%d.%m.%Y')
    
    # 1. Računamo osnovni troslojni raspored iz pozadinske matematike
    df, dani = izracunaj_troslojni_raspored(fajl_baze)
    
    if df.empty:
        st.error("Podaci za raspored nisu uspešno učitani iz baze.")
        return

    # Inicijalizujemo fajl za ručne korekcije ako ne postoji
    if not os.path.exists(fajl_rucnih_promena) or os.path.getsize(fajl_rucnih_promena) == 0:
        df_prazan = pd.DataFrame(columns=['ID MAŠINE', 'DATUM', 'NOVI VOZAČ'])
        df_prazan.to_csv(fajl_rucnih_promena, index=False)

    # Učitavamo spiskove vozača i mašina za čiste padajuće menije na vrhu
    opcije_radnika = [""]
    if os.path.exists('POSADA_BAZA.csv'):
        try:
            df_r = pd.read_csv('POSADA_BAZA.csv')
            if 'PREZIME I IME' in df_r.columns:
                opcije_radnika.extend(sorted(df_r['PREZIME I IME'].dropna().astype(str).unique()))
        except:
            pass

    opcije_masina = [""]
    if os.path.exists('GARAZA_BAZA.csv'):
        try:
            df_m = pd.read_csv('GARAZA_BAZA.csv')
            if 'GARAŽNI BROJ' in df_m.columns:
                opcije_masina.extend(sorted(df_m['GARAŽNI BROJ'].dropna().astype(str).unique()))
        except:
            pass

    # --- 🎯 POPRAVLJENO DUGME SA PRAVIM GRAFIČKIM KALENDAROM ZA URANJANJE ---
    with st.popover("📅 KORIGUJ RASPORED"):
        st.write("### Unesi brzu operativnu izmenu vozača")
        k_id = st.selectbox("Izaberi garažni broj mašine:", opcije_masina, key="kor_id")
        
        # OVO JE SADA PRAVI GRAFIČKI KALENDAR NA KLIK UNUTAR PROZORČIĆA
        k_datum_izbor = st.date_input("Izaberi datum za korekciju:", datetime.now().date(), key="kor_dat")
        k_dan = k_datum_izbor.strftime('%d.%m.%Y')
        
        k_radnik = st.selectbox("Izaberi novog vozača (Padajući meni):", opcije_radnika, key="kor_rad")
        
        if st.button("SAČUVAJ IZMENU", key="kor_btn"):
            if k_id and k_dan:
                try:
                    df_promene = pd.read_csv(fajl_rucnih_promena)
                except:
                    df_promene = pd.DataFrame(columns=['ID MAŠINE', 'DATUM', 'NOVI VOZAČ'])
                
                # Čistimo stare zapise za istu mašinu i isti dan da nema dupliranja
                df_promene = df_promene[~((df_promene['ID MAŠINE'] == str(k_id).strip().upper()) & (df_promene['DATUM'] == str(k_dan).strip()))]
                
                # Upisujemo novu korekciju
                novi_red = pd.DataFrame([{'ID MAŠINE': str(k_id).strip().upper(), 'DATUM': str(k_dan).strip(), 'NOVI VOZAČ': str(k_radnik).upper().strip()}])
                df_promene = pd.concat([df_promene, novi_red], ignore_index=True)
                df_promene.to_csv(fajl_rucnih_promena, index=False)
                st.success("Izmena uspešno upisana!")
                st.rerun()

    st.write("")

    # 2. Primenjujemo sačuvane ručne korekcije preko izračunatog rasporeda
    if os.path.exists(fajl_rucnih_promena):
        try:
            df_promene = pd.read_csv(fajl_rucnih_promena)
            for _, red_p in df_promene.iterrows():
                m_id = str(red_p['ID MAŠINE']).strip().upper()
                datum_p = str(red_p['DATUM']).strip()
                vozac_p = str(red_p['NOVI VOZAČ']).strip().upper()
                
                if datum_p in df.columns:
                    idx_m = df[df['ID MAŠINE'].astype(str).str.strip().str.upper() == m_id].index
                    if not idx_m.empty:
                        df.loc[idx_m, datum_p] = vozac_p
        except:
            pass

    osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
    
    # AUTOMATSKO CENTRIRANJE OKO DANAŠNJEG DANA UNUTAR OVIH 10 OPERATIVNIH DANA
    if danasnji_str in dani:
        idx_danas = dani.index(danasnji_str)
        poredjane_kolone = osnovne_kolone + dani[idx_danas-2:] + dani[:idx_danas-2]
    else:
        poredjane_kolone = osnovne_kolone + dani

    # Otvaramo mirnu i fiksiranu tabelu bez ikakvih kočenja i petlji
    st.data_editor(
        df,
        use_container_width=True,
        column_order=poredjane_kolone,
        column_config={
            "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True, disabled=True),
            "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True, disabled=True)
        },
        disabled=True,
        key="editor_troslojnog_rasporeda_fiksni_mirni"
    )
