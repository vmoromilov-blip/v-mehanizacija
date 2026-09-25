import pandas as pd
import os
from datetime import datetime, timedelta

# VEŽEMO SE STROGO ZA TVOJA TRI TAČNA FAJLA KOJA IMAMO NA LISTI
from RASPORED_TURNUS import povuci_redovne_turnuse
from RASPORED_SLOJ2 import primeni_filter_ispravnosti
from RASPORED_SLOJ3 import primeni_vojne_zamene

def izracunaj_troslojni_raspored(fajl_baze):
    danas = datetime.now()
    dani_dt = []
    
    # 🎯 OPERATIVNI PROZOR: 3 dana unazad, DANAS, 5 dana unapred
    for i in range(-3, 6):
        dani_dt.append(danas + timedelta(days=i))
        
    dani_dt.sort()
    dani = [d.strftime('%d.%m.%Y') for d in dani_dt]
        
    # Osiguravamo čitanje Garaže da nam ne sruši celi sistem
    df_final = pd.DataFrame()
    if os.path.exists('GARAZA_BAZA.csv'):
        try:
            df_g = pd.read_csv('GARAZA_BAZA.csv')
            df_g.columns = [c.upper().strip() for c in df_g.columns]
            kolona_gb = 'GARAŽNI BROJ' if 'GARAŽNI BROJ' in df_g.columns else df_g.columns[1] if len(df_g.columns) > 1 else df_g.columns[0]
            kolona_tip = 'TIP MAŠINE' if 'TIP MAŠINE' in df_g.columns else df_g.columns[0]
            
            df_final['MAŠINA'] = df_g[kolona_tip].astype(str).str.strip().str.upper()
            df_final['ID MAŠINE'] = df_g[kolona_gb].astype(str).str.strip().str.upper()
        except Exception as e:
            print(f"GREŠKA U ČITANJU GARAŽE: {e}")
            return pd.DataFrame(), dani
    else:
        return pd.DataFrame(), dani

    if df_final.empty:
        return df_final, dani

    for dan in dani:
        df_final[dan] = ""

    # 🚀 NEPROBOJNI LANAC: Svaki sloj umotavamo u zaštitu da kvar u bazi ne sruši ekran
    try:
        df_final = povuci_redovne_turnuse(df_final, dani)      # SLOJ 1
    except Exception as e:
        print(f"GREŠKA U SLOJU 1 (TURNUSI): {e}")

    try:
        df_final = primeni_filter_ispravnosti(df_final, dani)  # SLOJ 2
    except Exception as e:
        print(f"GREŠKA U SLOJU 2 (ISPRVNOST): {e}")

    try:
        df_final = primeni_vojne_zamene(df_final, dani)        # SLOJ 3
    except Exception as e:
        print(f"GREŠKA U SLOJU 3 (ZAMENE): {e}")

    return df_final.fillna(''), dani
