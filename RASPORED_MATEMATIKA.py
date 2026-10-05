import pandas as pd
import os
from datetime import datetime, timedelta

def izracunaj_smenski_turnus(start_str, turnus_tip, smena, trenutni_dt):
    try:
        start_dt = datetime.strptime(str(start_str).strip(), '%d.%m.%Y').date()
        if trenutni_dt >= start_dt:
            razlika_dana = (trenutni_dt - start_dt).days
            if str(turnus_tip).strip() == '1':
                return True
            elif str(turnus_tip).strip() == '5':
                ciklus = razlika_dana % 10
                if str(smena).strip().upper() == 'A':
                    return 0 <= ciklus < 5
                elif str(smena).strip().upper() == 'B':
                    return 5 <= ciklus < 10
    except:
        pass
    return False

def izracunaj_troslojni_raspored(fajl_baze):
    danas = datetime.now()
    dani_dt = []
    
    # 🎯 FIKSIRANI OPERATIVNI PROZOR: 3 dana unazad, DANAS, 5 dana unapred
    for i in range(-3, 6):
        dani_dt.append(danas + timedelta(days=i))
        
    dani_dt.sort()
    dani = [d.strftime('%d.%m.%Y') for d in dani_dt]
    
    df_final = pd.DataFrame()
    
    # Čitamo osnovnu strukturu mašina iz Garaže
    if os.path.exists('GARAZA_BAZA.csv'):
        try:
            df_g = pd.read_csv('GARAZA_BAZA.csv')
            df_g.columns = [c.upper().strip() for c in df_g.columns]
            kolona_gb = 'GARAŽNI BROJ' if 'GARAŽNI BROJ' in df_g.columns else df_g.columns[0]
            kolona_tip = 'TIP MAŠINE' if 'TIP MAŠINE' in df_g.columns else df_g.columns[1]
            
            df_final['MAŠINA'] = df_g[kolona_tip].astype(str).str.strip().str.upper()
            df_final['ID MAŠINE'] = df_g[kolona_gb].astype(str).str.strip().str.upper()
        except:
            pass

    if df_final.empty:
        return pd.DataFrame(), dani

    for dan in dani:
        df_final[dan] = ""

    # SLOJ 1: Povlačenje turnusa iz baze nosilaca
    if os.path.exists('nosioci_baza.csv'):
        try:
            df_n = pd.read_csv('nosioci_baza.csv')
            df_n.columns = [c.upper().strip() for c in df_n.columns]
            df_n['ID MAŠINE'] = df_n['ID MAŠINE'].astype(str).str.strip().str.upper()
            
            for dan in dani:
                trenutni_dt = datetime.strptime(dan, '%d.%m.%Y').date()
                for idx, red in df_final.iterrows():
                    m_id = str(red['ID MAŠINE']).strip().upper()
                    masina_nosioci = df_n[df_n['ID MAŠINE'] == m_id]
                    for _, n_red in masina_nosioci.iterrows():
                        start_str = str(n_red['START DATUM']).strip()
                        smena = str(n_red['SMENA']).strip().upper()
                        ime_vozača = str(n_red['NOSILAC']).strip().upper()
                        turnus_tip = str(n_red['TIP TURNUSA']).strip()
                        
                        if izracunaj_smenski_turnus(start_str, turnus_tip, smena, trenutni_dt):
                            df_final.at[idx, dan] = ime_vozača
        except:
            pass

    # SLOJ 2: Filter ispravnosti (Mirovanje i kvarovi prazne ćeliju)
    if os.path.exists('ispravnost_baza.csv'):
        try:
            df_isp = pd.read_csv('ispravnost_baza.csv')
            df_isp.columns = [str(c).strip().upper() for c in df_isp.columns]
            
            # Tražimo kolonu ključa tekstualno bez uzimanja celog niza kolona
            k_id = 'ID MAŠINE' if 'ID MAŠINE' in df_isp.columns else 'GARAŽNI BROJ' if 'GARAŽNI BROJ' in df_isp.columns else df_isp.columns[0]
            df_isp[k_id] = df_isp[k_id].astype(str).str.strip().str.upper()
            
            for dan in dani:
                dan_u = dan.upper()
                if dan_u in df_isp.columns:
                    for idx, red in df_final.iterrows():
                        m_id = str(red['ID MAŠINE']).strip().upper()
                        status_red = df_isp[df_isp[k_id] == m_id]
                        if not status_red.empty:
                            trenutni_status = str(status_red[dan_u].values[0]).strip().upper()
                            if trenutni_status in ['NE', 'MIR', 'VIK']:
                                df_final.at[idx, dan] = ""
        except:
            pass

    # SLOJ 3: Vojne zamene seku u dan precizno
    if os.path.exists('zamena.csv'):
        try:
            df_zam = pd.read_csv('zamena.csv')
            df_zam.columns = [c.upper().strip() for c in df_zam.columns]
            kolona_m = 'ID MAŠINE' if 'ID MAŠINE' in df_zam.columns else df_zam.columns[0]
            df_zam[kolona_m] = df_zam[kolona_m].astype(str).str.strip().str.upper()
            
            for dan in dani:
                trenutni_dt = datetime.strptime(dan, '%d.%m.%Y')
                for _, zam_red in df_zam.iterrows():
                    p_str = str(zam_red['DATUM POČETKA']).strip()
                    z_str = str(zam_red['DATUM ZAVRŠETKA']).strip()
                    try:
                        p_dt = datetime.strptime(p_str, '%Y-%m-%d') if '-' in p_str else datetime.strptime(p_str, '%d.%m.%Y')
                        z_dt = datetime.strptime(z_str, '%Y-%m-%d') if '-' in z_str else datetime.strptime(z_str, '%d.%m.%Y')
                        if p_dt.date() <= trenutni_dt.date() <= z_dt.date():
                            m_id = str(zam_red[kolona_m]).strip().upper()
                            idx_m = df_final[df_final['ID MAŠINE'] == m_id].index
                            if not idx_m.empty:
                                df_final.loc[idx_m, dan] = str(zam_red['ZAMENA']).upper().strip()
                    except:
                        pass
        except:
            pass

    return df_final.fillna(''), dani
