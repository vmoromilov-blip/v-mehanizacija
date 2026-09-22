import pandas as pd
import os
from datetime import datetime, timedelta

def izracunaj_troslojni_raspored(fajl_baze):
    # 1. Pravimo prozor od TAČNO 10 operativnih dana (5 unazad, danas, 4 unapred)
    danas = datetime.now()
    dani_dt = []
    for i in range(-5, 5):
        dani_dt.append(danas + timedelta(days=i))
        
    # Sortiramo ih strogo hronološki da datumi idu prirodno sleva nadesno
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

    # Pravimo kolone SAMO za ovih 10 operativnih dana
    for dan in dani:
        df_final[dan] = ""

    # --- SLOJ 1: Povlačenje redovnih nosilaca iz nove upeglane baze ---
    if os.path.exists('nosioci_baza.csv'):
        try:
            df_n = pd.read_csv('nosioci_baza.csv')
            df_n.columns = [c.upper().strip() for c in df_n.columns]
            df_n['ID MAŠINE'] = df_n['ID MAŠINE'].astype(str).str.strip().str.upper()
            
            for idx, red in df_final.iterrows():
                m_id = str(red['ID MAŠINE']).strip().upper()
                redovni = df_n[df_n['ID MAŠINE'] == m_id]
                if not redovni.empty:
                    ime_radnika = str(redovni.iloc[-1]['NOSILAC']).upper().strip()
                    if ime_radnika != "NAN" and ime_radnika != "":
                        for dan in dani:
                            df_final.at[idx, dan] = ime_radnika
        except:
            pass

    # --- 🎯 SLOJ 2: POPRAVLJENI FILTER ISPRVNOSTI (Čisti ćeliju ako je NE, MIR ili VIK) ---
    if os.path.exists('ispravnost_baza.csv'):
        try:
            df_isp = pd.read_csv('ispravnost_baza.csv')
            # Čistimo i osiguravamo nazive kolona i ID mašina
            df_isp.columns = [str(c).strip() for c in df_isp.columns]
            df_isp['ID MAŠINE'] = df_isp['ID MAŠINE'].astype(str).str.strip().str.upper()
            
            for dan in dani:
                # Tražimo kolonu u ispravnosti koja odgovara našem datumu
                kolona_ispravnosti = [c for c in df_isp.columns if c == dan]
                if kolona_ispravnosti:
                    c_dan = kolona_ispravnosti[0]
                    for idx, red in df_final.iterrows():
                        m_id = str(red['ID MAŠINE']).strip().upper()
                        status_red = df_isp[df_isp['ID MAŠINE'] == m_id]
                        if not status_red.empty:
                            trenutni_status = str(status_red[c_dan].values[0]).strip().upper()
                            # Ako osetimo bilo šta osim aktivnog rada, momentalno brišemo vozača!
                            if trenutni_status in ['NE', 'MIR', 'VIK']:
                                df_final.at[idx, dan] = ""
        except:
            pass

    # --- SLOJ 3: Vojna naredba iz Zamena (Prebrisavanje cells realnim stanjem) ---
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
