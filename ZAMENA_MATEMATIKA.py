import pandas as pd
import os

def ocisti_decimale_i_kolone(df):
    # Sređujemo nova imena kolona prema tvom diktatu
    df = df.rename(columns={
        'START DATUM': 'DATUM POČETKA', 'END DATUM': 'DATUM ZAVRŠETKA',
        'SAP BROJ': 'ID BROJ', 'SAP BROJ.1': 'ID BROJ 2',
        'SAP BROJ2': 'ID BROJ 2', 'ID BROJ.1': 'ID BROJ 2'
    })
    
    # Hirurški čistimo sve zareze i .0 decimalne viškove sa ID brojeva
    for col in df.columns:
        if 'ID BROJ' in str(col).upper():
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.replace('nan', '').str.strip()
    return df.fillna('')

def nadji_id_broj_radnika(ime_radnika):
    if os.path.exists('POSADA_BAZA.csv') and ime_radnika:
        try:
            df_r = pd.read_csv('POSADA_BAZA.csv')
            s = df_r[df_r['PREZIME I IME'] == ime_radnika]['SAP BROJ'].values
            if len(s) > 0 and pd.notna(s[0]):
                return str(int(float(s[0])))
        except:
            pass
    return ""
