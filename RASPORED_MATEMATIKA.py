import pandas as pd
import os
from datetime import datetime, timedelta
# Povezujemo Sloj 1 iz prve fioke
from RASPORED_TURNUS import povuci_redovne_turnuse

def primeni_filter_ispravnosti(df_final, dani):
    if not os.path.exists('ispravnost_baza.csv'):
        return df_final
    try:
        df_isp = pd.read_csv('ispravnost_baza.csv')
        df_isp.columns = [str(c).strip() for c in df_isp.columns]
        df_isp['ID MAŠINE'] = df_isp['ID MAŠINE'].astype(str).str.strip().str.upper()
        
        for dan in dani:
            if dan in df_isp.columns:
                for idx, red in df_final.iterrows():
                    m_id = str(red['ID MAŠINE']).strip().upper()
                    status_red = df_isp[df_isp['ID MAŠINE'] == m_id]
                    if not status_red.empty:
                        trenutni_status = str(status_red[dan].values).strip().upper()
                        if trenutni_status in ['NE', 'MIR', 'VIK']:
                            df_final.at[idx, dan] = ""
    except:
        pass
    return df_final

def primeni_vojne_zamene(df_final, dani):
    if not os.path.exists('zamena.csv'):
        return df_final
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
                    
                    # 🎯 Zamena važi samo ako dan strogo upada u opseg datuma
                    if p_dt.date() <= trenutni_dt.date() <= z_dt.date():
                        m_id = str(zam_red['ID MAŠINE']).strip().upper()
                        idx_m = df_final[df_final['ID MAŠINE'] == m_id].index
                        if not idx_m.empty:
                            df_final.loc[idx_m, dan] = str(zam_red['ZAMENA']).upper().strip()
                except:
                    pass
    except:
        pass
    return df_final

def izracunaj_troslojni_raspored(fajl_baze):
    danas = datetime.now()
    dani_dt = []
    
    # 🎯 FIKSIRANI OPERATIVNI PROZOR: 3 dana unazad, DANAS, 5 dana unapred
    for i in range(-3, 6):
        dani_dt.append(danas + timedelta(days=i))
        
    dani_dt.sort()
    dani = [d.strftime('%d.%m.%Y') for d in dani_dt]
        
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

    # 🚀 KOMPLETAN LANAC PRORAČUNA: Puštamo sva tri sloja po vojničkom redu
    df_final = povuci_redovne_turnuse(df_final, dani)      # SLOJ 1: Turnusi 5-5
    df_final = primeni_filter_ispravnosti(df_final, dani)  # SLOJ 2: Kvarovi i mirovanja
    df_final = primeni_vojne_zamene(df_final, dani)        # SLOJ 3: Zamene u dan

    return df_final.fillna(''), dani
