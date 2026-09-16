import pandas as pd
import os

def primeni_filter_ispravnosti(df_final, dani):
    fajl_csv = "ispravnost_baza.csv"
    
    # Ako imamo našu živu internet bazu ispravnosti u fascikli
    if os.path.exists(fajl_csv):
        try:
            df_isp = pd.read_csv(fajl_csv)
            # Čistimo garažne brojeve radi tačnog prepoznavanja
            df_isp['ID MAŠINE'] = df_isp['ID MAŠINE'].astype(str).str.strip()
            
            # Proveravamo ispravnost samo za ovih 10 operativnih dana
            for dan in dani:
                if dan in df_isp.columns:
                    for idx, red in df_final.iterrows():
                        m_id = str(red['ID MAŠINE']).strip()
                        status_red = df_isp[df_isp['ID MAŠINE'] == m_id]
                        
                        if not status_red.empty:
                            # Čitamo status mašine za taj konkretan dan
                            trenutni_status = str(status_red[dan].values[0]).strip().upper()
                            # Ako je mašina u kvaru (NE), leži (MIR) ili je neradni dan (VIK), brišemo rukovaoca
                            if trenutni_status in ['NE', 'MIR', 'VIK']:
                                df_final.at[idx, dan] = ""
        except:
            pass
            
    return df_final
