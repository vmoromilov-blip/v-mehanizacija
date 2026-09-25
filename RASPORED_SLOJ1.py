import pandas as pd
import os
from datetime import datetime
from RASPORED_TURNUS import izracunaj_smenski_turnus

def povuci_redovne_turnuse(df_final, dani):
    if not os.path.exists('nosioci_baza.csv'):
        return df_final
        
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
        
    return df_final

