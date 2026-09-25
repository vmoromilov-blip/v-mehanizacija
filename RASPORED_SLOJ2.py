import pandas as pd
import os

def primeni_filter_ispravnosti(df_final, dani):
    if not os.path.exists('ispravnost_baza.csv'):
        return df_final
        
    try:
        df_isp = pd.read_csv('ispravnost_baza.csv')
        df_isp.columns = [str(c).strip() for c in df_isp.columns]
        
        # Tražimo tačnu kolonu sa ID-jem mašine na osnovu sadržaja
        kolona_id = None
        for c in df_isp.columns:
            if c.upper() in ['ID MAŠINE', 'GARAŽNI BROJ', 'ID MASINE']:
                kolona_id = c
                break
        if not kolona_id:
            kolona_id = df_isp.columns[1] if len(df_isp.columns) > 1 else df_isp.columns[0]
            
        df_isp[kolona_id] = df_isp[kolona_id].astype(str).str.strip().str.upper()
        
        for dan in dani:
            if dan in df_isp.columns:
                for idx, red in df_final.iterrows():
                    m_id = str(red['ID MAŠINE']).strip().upper()
                    status_red = df_isp[df_isp[kolona_id] == m_id]
                    if not status_red.empty:
                        trenutni_status = str(status_red[dan].values[0]).strip().upper()
                        if trenutni_status in ['NE', 'MIR', 'VIK']:
                            df_final.at[idx, dan] = ""
    except:
        pass
        
    return df_final
