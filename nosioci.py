import pandas as pd
import os
from datetime import datetime

def izracunaj_aktivnog_nosioca(fajl_baze, datum_za_proveru_str):
    fajl_csv = "nosioci_baza.csv"
    if os.path.exists(fajl_csv):
        df_nosioci = pd.read_csv(fajl_csv)
    elif os.path.exists(fajl_baze):
        df_nosioci = pd.read_excel(fajl_baze, sheet_name='NOSIOCI')
        df_nosioci.to_csv(fajl_csv, index=False)
    else:
        return {}

    df_nosioci = df_nosioci.rename(columns={'START DATUM': 'DATUM POČETKA'})
    datum_meta = datetime.strptime(datum_za_proveru_str, '%d.%m.%Y')
    dan_u_nedelji = datum_meta.weekday()
    
    aktivni_na_masinama = {}
    
    for masina_id, grupa in df_nosioci.groupby('ID MAŠINE'):
        smena_a = grupa[grupa['SMENA'].str.upper() == 'A'] if 'SMENA' in grupa.columns else pd.DataFrame()
        smena_b = grupa[grupa['SMENA'].str.upper() == 'B'] if 'SMENA' in grupa.columns else pd.DataFrame()
        
        if grupa.empty:
            continue
            
        prvi_red = grupa.iloc[0]
        turnus = int(prvi_red['TIP TURNUSA']) if 'TIP TURNUSA' in grupa.columns and pd.notna(prvi_red['TIP TURNUSA']) else 1
        
        try:
            start_dt_str = str(prvi_red['DATUM POČETKA']).split()[0]
            start_dt = datetime.strptime(start_dt_str, '%Y-%m-%d')
        except:
            start_dt = datetime(2026, 1, 1)
            
        razlika_u_danima = (datum_meta - start_dt).days
        m_id_str = str(masina_id).strip()
        
        if turnus == 1:
            if dan_u_nedelji < 5:
                if not smena_a.empty:
                    aktivni_na_masinama[m_id_str] = str(smena_a.iloc[0]['NOSILAC']).upper()
            else:
                aktivni_na_masinama[m_id_str] = ""
        else:
            if razlika_u_danima >= 0:
                pozicija_u_ciklusu = razlika_u_danima % (turnus * 2)
                if pozicija_u_ciklusu < turnus:
                    if not smena_a.empty:
                        aktivni_na_masinama[m_id_str] = str(smena_a.iloc[0]['NOSILAC']).upper()
                else:
                    if not smena_b.empty:
                        aktivni_na_masinama[m_id_str] = str(smena_b.iloc[0]['NOSILAC']).upper()
                    elif not smena_a.empty:
                        aktivni_na_masinama[m_id_str] = ""
            else:
                if not smena_a.empty:
                    aktivni_na_masinama[m_id_str] = str(smena_a.iloc[0]['NOSILAC']).upper()

    return aktivni_na_masinama
