import pandas as pd
import os
from datetime import datetime, timedelta

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

    # --- 🎯 SLOJ 1: NOVI SAMOSTALNI TURNUS MOTOR (RITAM 5 RADI - 5 LADI ZA SVAKI DAN) ---
    if os.path.exists('nosioci_baza.csv'):
        try:
            df_n = pd.read_csv('nosioci_baza.csv')
            df_n.columns = [c.upper().strip() for c in df_n.columns]
            df_n['ID MAŠINE'] = df_n['ID MAŠINE'].astype(str).str.strip().str.upper()
            
            for dan in dani:
                trenutni_dt = datetime.strptime(dan, '%d.%m.%Y').date()
                
                for idx, red in df_final.iterrows():
                    m_id = str(red['ID MAŠINE']).strip().upper()
                    # Tražimo sve nosioce zavedene za ovu konkretnu mašinu
                    masina_nosioci = df_n[df_n['ID MAŠINE'] == m_id]
                    
                    for _, n_red in masina_nosioci.iterrows():
                        start_str = str(n_red['START DATUM']).strip()
                        smena = str(n_red['SMENA']).strip().upper()
                        ime_vozača = str(n_red['NOSILAC']).strip().upper()
                        turnus_tip = str(n_red['TIP TURNUSA']).strip()
                        
                        try:
                            start_dt = datetime.strptime(start_str, '%d.%m.%Y').date()
                            if trenutni_dt >= start_dt:
                                razlika_dana = (trenutni_dt - start_dt).days
                                
                                # Ako je turnus 1 - čovek radi svaki dan bez pauze (Nosioci)
                                if turnus_tip == '1':
                                    df_final.at[idx, dan] = ime_vozača
                                
                                # Ako je turnus 5 - računamo ritam 5 dana rada, 5 dana odmora
                                elif turnus_tip == '5':
                                    ciklus = razlika_dana % 10
                                    
                                    if smena == 'A':
                                        # Smena A radi prvih 5 dana u ciklusu od 10 dana
                                        if 0 <= ciklus < 5:
                                            df_final.at[idx, dan] = ime_vozača
                                    elif smena == 'B':
                                        # Smena B radi drugih 5 dana u ciklusu od 10 dana
                                        if 5 <= ciklus < 10:
                                            df_final.at[idx, dan] = ime_vozača
                        except:
                            pass
        except:
            pass

    # --- SLOJ 2: Filter ispravnosti (Brišemo vozača ako je mašina NE, MIR ili VIK) ---
    if os.path.exists('ispravnost_baza.csv'):
        try:
            df_isp = pd.read_csv('ispravnost_baza.csv')
            df_isp.columns = [str(c).strip() for c in df_isp.columns]
            df_isp['ID MAŠINE'] = df_isp['ID MAŠINE'].astype(str).str.strip().str.upper()
            
            for dan in dani:
                kolona_ispravnosti = [c for c in df_isp.columns if c == dan]
                if kolona_ispravnosti:
                    c_dan = kolona_ispravnosti
                    for idx, red in df_final.iterrows():
                        m_id = str(red['ID MAŠINE']).strip().upper()
                        status_red = df_isp[df_isp['ID MAŠINE'] == m_id]
                        if not status_red.empty:
                            trenutni_status = str(status_red[c_dan].values).strip().upper()
                            if trenutni_status in ['NE', 'MIR', 'VIK']:
                                df_final.at[idx, dan] = ""
        except:
            pass

    # --- SLOJ 3: Vojna naredba iz Zamena (Strogo sečenje u dan prema zadatom opsegu) ---
    if os.path.exists('zamena.csv'):
        try:
            df_zam = pd.read_csv('zamena.csv')
            df_zam.columns = [c.upper().strip() for c in df_zam.columns]
            
            for dan in dani:
                trenutni_dt = datetime.strptime(dan, '%d.%m.%Y')
                for _, zam_red in df_zam.iterrows():
                    p_str = str(zam_red['DATUM POČETKA']).strip()
                    z_str = str(zam_red['DATUM ZAVRŠETKA']).strip()
                    
                    try:
                        p_dt = datetime.strptime(p_str, '%Y-%m-%d') if '-' in p_str else datetime.strptime(p_str, '%d.%m.%Y')
                        z_dt = datetime.strptime(z_str, '%Y-%m-%d') if '-' in z_str else datetime.strptime(z_str, '%d.%m.%Y')
                        
                        if p_dt.date() <= trenutni_dt.date() <= z_dt.date():
                            m_id = str(zam_red['ID MAŠINE']).strip().upper()
                            idx_m = df_final[df_final['ID MAŠINE'] == m_id].index
                            if not idx_m.empty:
                                df_final.loc[idx_m, dan] = str(zam_red['ZAMENA']).upper().strip()
                    except:
                        pass
        except:
            pass

    return df_final.fillna(''), dani
