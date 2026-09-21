import pandas as pd
import os
from datetime import datetime

def inicijalizuj_bazu_ispravnosti(fajl_baze, fajl_csv):
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
    df['ID MAŠINE'] = df['ID MAŠINE'].astype(str).str.strip().str.upper()
    sve_nove_masine = set()

    # 1. Čitamo mašine iz Garaže (GARAZA_BAZA.csv)
    if os.path.exists('GARAZA_BAZA.csv'):
        try:
            df_g = pd.read_csv('GARAZA_BAZA.csv')
            df_g.columns = [c.upper().strip() for c in df_g.columns]
            kolona_gb = 'GARAŽNI BROJ' if 'GARAŽNI BROJ' in df_g.columns else df_g.columns
            kolona_tip = 'TIP MAŠINE' if 'TIP MAŠINE' in df_g.columns else df_g.columns
            for _, r in df_g.iterrows():
                gb = str(r[kolona_gb]).strip().upper()
                tip = str(r[kolona_tip]).strip().upper()
                if gb != "" and gb != "NAN":
                    sve_nove_masine.add((gb, tip))
        except:
            pass

    # 2. Čitamo mašine iz Zamena (zamena.csv) da nam ne promakne tvoj novi kiper VM!
    if os.path.exists('zamena.csv'):
        try:
            df_z = pd.read_csv('zamena.csv')
            df_z.columns = [c.upper().strip() for c in df_z.columns]
            if 'ID MAŠINE' in df_z.columns:
                for _, r in df_z.iterrows():
                    gb = str(r['ID MAŠINE']).strip().upper()
                    if gb != "" and gb != "NAN" and gb not in df['ID MAŠINE'].values:
                        sve_nove_masine.add((gb, "KIPER TEST"))
        except:
            pass

    # 3. Lepimo sve pronađene nove mašine na dno kalendara ispravnosti
    ažurirano = False
    for gb, tip in sve_nove_masine:
        if gb not in df['ID MAŠINE'].values:
            novi_red = {'MAŠINA': tip, 'ID MAŠINE': gb}
            for col in df.columns:
                if col not in ['MAŠINA', 'ID MAŠINE']:
                    novi_red[col] = 'DA'
            df = pd.concat([df, pd.DataFrame([novi_red])], ignore_index=True)
            ažurirano = True

    if ažurirano:
        df.to_csv(fajl_csv, index=False)
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
