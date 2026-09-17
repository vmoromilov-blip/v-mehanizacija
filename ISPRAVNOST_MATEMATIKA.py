import pandas as pd
import os
from datetime import datetime

def inicijalizuj_bazu_ispravnosti(fajl_baze, fajl_csv):
    # Čitamo iz Excela samo ako brza baza u fascikli već ne postoji (leči treptanje)
    if not os.path.exists(fajl_csv) or os.path.getsize(fajl_csv) == 0:
        if os.path.exists(fajl_baze):
            try:
                df = pd.read_excel(fajl_baze, sheet_name='ISPRAVNOST')
                df = df.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
                df.columns = [col.strftime('%d.%m.%Y') if isinstance(col, datetime) else str(col) for col in df.columns]
                df.to_csv(fajl_csv, index=False)
            except:
                pass

def dodaj_nova_vozila_u_ispravnost(df, fajl_csv):
    fajl_zivih = 'spisak_mašina.csv' if os.path.exists('spisak_mašina.csv') else ('spisak_masina.csv' if os.path.exists('spisak_masina.csv') else '')
    if fajl_zivih != "":
        try:
            df_zive = pd.read_csv(fajl_zivih)
            df_zive.columns = [c.upper().strip() for c in df_zive.columns]
            
            kolona_gb = 'GARAŽNI BROJ' if 'GARAŽNI BROJ' in df_zive.columns else ('GARAŽNI_BROJ' if 'GARAŽNI_BROJ' in df_zive.columns else df_zive.columns[1])
            kolona_tip = 'TIP MAŠINE' if 'TIP MAŠINE' in df_zive.columns else ('TIP_MAŠINE' if 'TIP_MAŠINE' in df_zive.columns else df_zive.columns[0])
            
            df['ID MAŠINE'] = df['ID MAŠINE'].astype(str).str.strip().str.upper()
            ažurirano = False
            
            for _, red in df_zive.iterrows():
                gb = str(red[kolona_gb]).strip().upper()
                tip = str(red[kolona_tip]).strip().upper()
                
                if gb != "" and gb != "NAN" and gb not in df['ID MAŠINE'].values:
                    novi_red = {'MAŠINA': tip, 'ID MAŠINE': gb}
                    for col in df.columns:
                        if col not in ['MAŠINA', 'ID MAŠINE']:
                            novi_red[col] = 'DA'
                    df = pd.concat([df, pd.DataFrame([novi_red])], ignore_index=True)
                    ažurirano = True
            
            if ažurirano:
                df.to_csv(fajl_csv, index=False)
        except:
            pass
    return df

def izvrsi_projektovanje_ispravnosti(df, p_masina, p_datum_str, p_status, fajl_csv):
    if p_datum_str in df.columns:
        df['ID MAŠINE'] = df['ID MAŠINE'].astype(str).str.strip().str.upper()
        idx = df[df['ID MAŠINE'] == str(p_masina).strip().upper()].index
        if not idx.empty:
            sve_kolone = list(df.columns)
            start_idx = sve_kolone.index(p_datum_str)
            for c in sve_kolone[start_idx:]:
                df.loc[idx, c] = p_status
            df.to_csv(fajl_csv, index=False)
            return True
    return False
