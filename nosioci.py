import pandas as pd
import os
from datetime import datetime

def izracunaj_aktivnog_nosioca(fajl_baze, datum_za_proveru_str):
    # Učitavamo živu bazu nosilaca iz fascikle
    fajl_csv = "nosioci_baza.csv"
    if os.path.exists(fajl_csv):
        df_nosioci = pd.read_csv(fajl_csv)
    elif os.path.exists(fajl_baze):
        df_nosioci = pd.read_excel(fajl_baze, sheet_name='NOSIOCI')
        df_nosioci.to_csv(fajl_csv, index=False)
    else:
        return {}

    # Čistimo nazive kolona
    df_nosioci = df_nosioci.rename(columns={'START DATUM': 'DATUM POČETKA'})
    
    datum_meta = datetime.strptime(datum_za_proveru_str, '%d.%m.%Y')
    dan_u_nedelji = datum_meta.weekday() # 0=Ponedeljak, 4=Petak, 5=Subota, 6=Nedelja
    
    aktivni_na_masinama = {}
    
    # Grupišemo nosioce po mašinama (jer imamo Smenu A i Smenu B)
    for masina_id, grupa in df_nosioci.groupby('ID MAŠINE'):
        smena_a = grupa[grupa['SMENA'].str.upper() == 'A'] if 'SMENA' in grupa.columns else pd.DataFrame()
        smena_b = grupa[grupa['SMENA'].str.upper() == 'B'] if 'SMENA' in grupa.columns else pd.DataFrame()
        
        # Uzimamo parametre iz prvog reda za tu mašinu
        prvi_red = grupa.iloc[0]
        turnus = int(prvi_red['TIP TURNUSA']) if 'TIP TURNUSA' in grupa.columns and pd.notna(prvi_red['TIP TURNUSA']) else 1
        
        try:
            start_dt_str = str(prvi_red['DATUM POČETKA']).split()[0]
            start_dt = datetime.strptime(start_dt_str, '%Y-%m-%d')
        except:
            start_dt = datetime(2026, 1, 1)
            
        # Računamo koliko je dana prošlo od nultog datuma do današnjeg dana
        razlika_u_danima = (datum_meta - start_dt).days
        
        # LOGIKA TURNUSA 1: Klasična smena ponedeljak-petak
        if turnus == 1:
            if dan_u_nedelji < 5: # Ponedeljak - Petak radi Smena A
                if not smena_a.empty:
                    aktivni_na_masinama[str(masina_id)] = str(smena_a.iloc[0]['NOSILAC'])
            else:
                aktivni_na_masinama[str(masina_id)] = "VIKEND"
                
        # LOGIKA TURNUSA X (npr. 5): X dana radiš, X dana ladiš
        else:
            if razlika_u_danima >= 0:
                # Delimo ukupne dane sa dužinom ciklusa (npr. za turnus 5, pun ciklus rada i odmora je 10 dana)
                pozicija_u_ciklusu = razlika_u_danima % (turnus * 2)
                
                if pozicija_u_ciklusu < turnus:
                    # Prvih X dana radi Smena A
                    if not smena_a.empty:
                        aktivni_na_masinama[str(masina_id)] = str(smena_a.iloc[0]['NOSILAC'])
                else:
                    # Drugih X dana upada Smena B (Kolega menja stražu)
                    if not smena_b.empty:
                        aktivni_na_masinama[str(masina_id)] = str(smena_b.iloc[0]['NOSILAC'])
                    elif not smena_a.empty:
                        aktivni_na_masinama[str(masina_id)] = "SLOBODAN DAN"
            else:
                if not smena_a.empty:
                    aktivni_na_masinama[str(masina_id)] = str(smena_a.iloc[0]['NOSILAC'])

    return aktivni_na_masinama
