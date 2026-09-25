import pandas as pd
import os
from datetime import datetime, timedelta

# VEŽEMO SE STROGO ZA TVOJA TRI KREIRANA FAJLA SA LEVE LISTE
from RASPORED_SLOJ1 import povuci_redovne_turnuse
from RASPORED_SLOJ2 import primeni_filter_ispravnosti
from RASPORED_SLOJ3 import primeni_vojne_zamene

def izracunaj_troslojni_raspored(fajl_baze):
    danas = datetime.now()
    dani_dt = []
    
    # 🎯 TVOJ OPERATIVNI PROZOR: 3 dana unazad, DANAS, 5 dana unapred (Ukupno 9 dana)
    for i in range(-3, 6):
        dani_dt.append(danas + timedelta(days=i))
        
    dani_dt.sort()
    dani = [d.strftime('%d.%m.%Y') for d in dani_dt]
        
    # Čitamo osnovnu strukturu mašina iz Garaže
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

    # 🚀 POVEZIVANJE U STRUGI VOJNIČKI LANAC PO TVOJIM SLOJEVIMA:
    df_final = povuci_redovne_turnuse(df_final, dani)      # Poziva SLOJ 1
    df_final = primeni_filter_ispravnosti(df_final, dani)  # Poziva SLOJ 2
    df_final = primeni_vojne_zamene(df_final, dani)        # Poziva SLOJ 3

    return df_final.fillna(''), dani
