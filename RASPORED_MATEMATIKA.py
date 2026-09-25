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
    
    df_final = pd.DataFrame()
    
    # 🚀 REVOLUCIONARNA ZAŠTITA: Ako fali brzi CSV, čitamo direktno originalni Excel plan!
    if os.path.exists('GARAZA_BAZA.csv'):
        try:
            df_g = pd.read_csv('GARAZA_BAZA.csv')
            df_g.columns = [c.upper().strip() for c in df_g.columns]
            kolona_gb = 'GARAŽNI BROJ' if 'GARAŽNI BROJ' in df_g.columns else df_g.columns[1]
            kolona_tip = 'TIP MAŠINE' if 'TIP MAŠINE' in df_g.columns else df_g.columns[0]
            
            df_final['MAŠINA'] = df_g[kolona_tip].astype(str).str.strip().str.upper()
            df_final['ID MAŠINE'] = df_g[kolona_gb].astype(str).str.strip().str.upper()
        except:
            pass

    # Ako je CSV zakazao ili je prazan, vadimo podatke direktno iz živog Excela 'plan.xlsm'
    if df_final.empty and os.path.exists(fajl_baze):
        try:
            df_excel = pd.read_excel(fajl_baze, sheet_name='SPISAK MAŠINA')
            df_excel.columns = [c.upper().strip() for c in df_excel.columns]
            kolona_gb = 'GARAŽNI BROJ' if 'GARAŽNI BROJ' in df_excel.columns else df_excel.columns[1]
            kolona_tip = 'TIP MAŠINE' if 'TIP MAŠINE' in df_excel.columns else df_excel.columns[0]
            
            df_final['MAŠINA'] = df_excel[kolona_tip].astype(str).str.strip().str.upper()
            df_final['ID MAŠINE'] = df_excel[kolona_gb].astype(str).str.strip().str.upper()
            # Usput pravimo svež CSV da popravimo memoriju servera
            df_final.to_csv('GARAZA_BAZA.csv', index=False)
        except:
            pass

    # Ako nemamo ništa, vraćamo prazno da ne puca sajt
    if df_final.empty:
        return pd.DataFrame(), dani

    for dan in dani:
        df_final[dan] = ""

    # 🚀 SIGURNI LANAC: Svaki sloj izvršavamo bezbedno
    try:
        df_final = povuci_redovne_turnuse(df_final, dani)      # SLOJ 1
    except:
        pass

    try:
        df_final = primeni_filter_ispravnosti(df_final, dani)  # SLOJ 2
    except:
        pass

    try:
        df_final = primeni_vojne_zamene(df_final, dani)        # SLOJ 3
    except:
        pass

    return df_final.fillna(''), dani
