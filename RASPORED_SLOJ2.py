import pandas as pd
import os

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
                        # Ako mašina leži, u kvaru je ili je vikend, ćelija se prazni
                        if trenutni_status in ['NE', 'MIR', 'VIK']:
                            df_final.at[idx, dan] = ""
    except:
        pass
        
    return df_final

