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
    sve_aktivne_masine = set()
    cisti_aktivni_gb = []

    # 1. Čitamo mašine koje stvarno postoje u Garaži (GARAZA_BAZA.csv)
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
                    sve_aktivne_masine.add((gb, tip))
                    cisti_aktivni_gb.append(gb)
        except:
            pass

    # 🚀 POPRAVLJENA OPERATIVNA METLA: Čistimo sve ručne unose kojih više nema u Garaži!
    if len(cisti_aktivni_gb) > 0:
        # Zadržavamo samo fabričke mašine iz originalnog Excela (koje imaju dugačke nazive)
        # ILI mašine koje se trenutno nalaze na tvom spisku u GARAŽI!
        # Ovo će bezuslovno obrisati kiper VM 123-VM jer više nije u Garaži!
        df_procešćen = df[(df['ID MAŠINE'].isin(cisti_aktivni_gb)) | (df['ID MAŠINE'].str.len() > 12)].copy()
        
        if len(df_procešćen) != len(df):
            df = df_procešćen
            df.to_csv(fajl_csv, index=False)

    # 2. Dodajemo nova vozila ako si ih regularno upisao u Garažu
    ažurirano = False
    for gb, tip in sve_aktivne_masine:
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
