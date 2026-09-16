import pandas as pd
import os
from datetime import datetime, timedelta
from nosioci import izracunaj_aktivnog_nosioca

def generisi_bazu_rasporeda(fajl_baze):
    # 1. Pravimo spisak od 10 ključnih dana (5 unazad, danas, 4 unapred)
    danas = datetime.now()
    dani = []
    for i in range(-5, 5):
        tekuci_dan = danas + timedelta(days=i)
        dani.append(tekuci_dan.strftime('%d.%m.%Y'))
        
    # 2. Čitamo osnovnu strukturu mašina
    if os.path.exists(fajl_baze):
        df_osnova = pd.read_excel(fajl_baze, sheet_name='RASPORED')
        df_osnova = df_osnova.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
        df_final = df_osnova[['MAŠINA', 'ID MAŠINE']].copy()
    else:
        # Ako nema Excela, gledamo naš CSV sa plusića
        if os.path.exists('spisak_masina.csv'):
            df_osnova = pd.read_csv('spisak_masina.csv')
        elif os.path.exists('spisak_mašina.csv'):
            df_osnova = pd.read_csv('spisak_mašina.csv')
        else:
            df_osnova = pd.DataFrame(columns=['TIP MAŠINE', 'GARAŽNI BROJ'])
        df_final = df_osnova.rename(columns={'TIP MAŠINE': 'MAŠINA', 'GARAŽNI BROJ': 'ID MAŠINE'})

    # 3. Dodajemo mašine koje si uneo na plusić, ako već nisu u tabeli
    fajl_zivih = 'spisak_mašina.csv' if os.path.exists('spisak_mašina.csv') else ('spisak_masina.csv' if os.path.exists('spisak_masina.csv') else '')
    if fajl_zivih != "":
        try:
            df_zive = pd.read_csv(fajl_zivih)
            for _, red in df_zive.iterrows():
                gb = str(red['GARAŽNI BROJ']).strip()
                tip = str(red['TIP MAŠINE']).strip()
                if gb not in df_final['ID MAŠINE'].astype(str).str.strip().values:
                    df_final = pd.concat([df_final, pd.DataFrame([{'MAŠINA': tip, 'ID MAŠINE': gb}])], ignore_index=True)
        except:
            pass

    # 4. Punimo kolone za ovih 10 dana imenima nosilaca iz turnusa
    for dan in dani:
        df_final[dan] = ""
        nosioci_za_dan = izracunaj_aktivnog_nosioca(fajl_baze, dan)
        for idx, red in df_final.iterrows():
            m_id = str(red['ID MAŠINE']).strip()
            if m_id in nosioci_za_dan:
                df_final.at[idx, dan] = nosioci_za_dan[m_id]
                
    return df_final, dani
