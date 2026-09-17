import pandas as pd
import os
from datetime import datetime, timedelta
from nosioci import izracunaj_aktivnog_nosioca

def izracunaj_troslojni_raspored(fajl_baze):
    # 1. Pravimo prozor od 10 operativnih dana (5 unazad, danas, 4 unapred)
    danas = datetime.now()
    dani = []
    for i in range(-5, 5):
        tekuci_dan = danas + timedelta(days=i)
        dani.append(tekuci_dan.strftime('%d.%m.%Y'))
        
    # 2. Izvlačimo osnovnu strukturu mašina iz Garaže (GARAZA_BAZA.csv)
    if os.path.exists('GARAZA_BAZA.csv'):
        df_g = pd.read_csv('GARAZA_BAZA.csv')
        df_g.columns = [c.upper().strip() for c in df_g.columns]
        kolona_gb = 'GARAŽNI BROJ' if 'GARAŽNI BROJ' in df_g.columns else ('GARAŽNI_BROJ' if 'GARAŽNI_BROJ' in df_g.columns else df_g.columns[1])
        kolona_tip = 'TIP MAŠINE' if 'TIP MAŠINE' in df_g.columns else ('TIP_MAŠINE' if 'TIP_MAŠINE' in df_g.columns else df_g.columns[0])
        df_final = pd.DataFrame()
        df_final['MAŠINA'] = df_g[kolona_tip].astype(str).str.strip().str.upper()
        df_final['ID MAŠINE'] = df_g[kolona_gb].astype(str).str.strip().str.upper()
    else:
        return pd.DataFrame(), dani

    # Dodajemo kolone za ovih 10 operativnih dana
    for dan in dani:
        df_final[dan] = ""

    # SLOJ 1: Popunjavamo stalne nosioce iz turnusa
    for dan in dani:
        nosioci_za_dan = izracunaj_aktivnog_nosioca(fajl_baze, dan)
        for idx, red in df_final.iterrows():
            m_id = str(red['ID MAŠINE']).strip().upper()
            if m_id in nosioci_za_dan:
                df_final.at[idx, dan] = str(nosioci_za_dan[m_id]).upper().strip()

    # SLOJ 2: Proveravamo ispravnost_baza.csv i brišemo ljude ako je mašina NE, MIR, VIK
    if os.path.exists('ispravnost_baza.csv'):
        try:
            df_isp = pd.read_csv('ispravnost_baza.csv')
            df_isp['ID MAŠINE'] = df_isp['ID MAŠINE'].astype(str).str.strip().str.upper()
            for dan in dani:
                if dan in df_isp.columns:
                    for idx, red in df_final.iterrows():
                        m_id = str(red['ID MAŠINE']).strip().upper()
                        status_red = df_isp[df_isp['ID MAŠINE'] == m_id]
                        if not status_red.empty:
                            trenutni_status = str(status_red[dan].values[0]).strip().upper()
                            if trenutni_status in ['NE', 'MIR', 'VIK']:
                                df_final.at[idx, dan] = ""
        except:
            pass

    # SLOJ 3: Primenjujemo izričitu vojnu naredbu iz Zamena (zamena.csv)
    if os.path.exists('zamena.csv'):
        try:
            df_zam = pd.read_csv('zamena.csv')
            for dan in dani:
                trenutni_dt = datetime.strptime(dan, '%d.%m.%Y')
                for _, zam_red in df_zam.iterrows():
                    p_str = str(zam_red['DATUM POČETKA']).strip()
                    z_str = str(zam_red['DATUM ZAVRŠETKA']).strip()
                    p_dt = datetime.strptime(p_str, '%Y-%m-%d') if '-' in p_str else datetime.strptime(p_str, '%d.%m.%Y')
                    z_dt = datetime.strptime(z_str, '%Y-%m-%d') if '-' in z_str else datetime.strptime(z_str, '%d.%m.%Y')
                    
                    if p_dt <= trenutni_dt <= z_dt:
                        m_id = str(zam_red['ID MAŠINE']).strip().upper()
                        idx_m = df_final[df_final['ID MAŠINE'] == m_id].index
                        if not idx_m.empty:
                            df_final.loc[idx_m, dan] = str(zam_red['ZAMENA']).upper().strip()
        except:
            pass

    return df_final.fillna(''), dani
