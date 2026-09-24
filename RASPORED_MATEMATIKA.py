import pandas as pd
import os
from datetime import datetime, timedelta

# UVOZIMO SVA TRI NAŠA NOVA PROČIŠĆENA SLOJA OD JUČE I DANAS
from RASPORED_SLOJ1 import povuci_redovne_turnuse
from RASPORED_SLOJ2 import primeni_filter_ispravnosti
from RASPORED_SLOJ3 import primeni_vojne_zamene

def izracunaj_troslojni_raspored(fajl_baze):
    # 1. Pravimo prozor od TAČNO 10 operativnih dana (5 unazad, danas, 4 unapred)
    danas = datetime.now()
    dani_dt = []
    for i in range(-5, 5):
        dani_dt.append(danas + timedelta(days=i))
        
    dani_dt.sort()
    dani = [d.strftime('%d.%m.%Y') for d in dani_dt]
        
    # 2. Brzo čitanje osnovne strukture mašina iz Garaže
    if os.path.exists('GARAZA_BAZA.csv'):
        try:
            df_g = pd.read_csv('GARAZA_BAZA.csv')
            df_g.columns = [c.upper().strip() for c in df_g.columns]
            kolona_gb = 'GARAŽNI BROJ' if 'GARAŽNI BROJ' in df_g.columns else df_g.columns
            kolona_tip = 'TIP MAŠINE' if 'TIP MAŠINE' in df_g.columns else df_g.columns
            df_final = pd.DataFrame()
            df_final['MAŠINA'] = df_g[kolona_tip].astype(str).str.strip().str.upper()
            df_final['ID MAŠINE'] = df_g[kolona_gb].astype(str).str.strip().str.upper()
        except:
            return pd.DataFrame(), dani
    else:
        return pd.DataFrame(), dani

    for dan in dani:
        df_final[dan] = ""

    # 🚀 VOJNIČKI LANAC: Puštamo slojeve da rade tačno tvojim redosledom
    df_final = povuci_redovne_turnuse(df_final, dani)      # SLOJ 1: Turnusi 5-5
    df_final = primeni_filter_ispravnosti(df_final, dani)  # SLOJ 2: Mirovanje i kvarovi
    df_final = primeni_vojne_zamene(df_final, dani)        # SLOJ 3: Zamene u dan

    return df_final.fillna(''), dani
