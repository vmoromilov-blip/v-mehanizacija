import pandas as pd
import os
from datetime import datetime

def primeni_vojne_zamene(df_final, dani):
    if not os.path.exists('zamena.csv'):
        return df_final
        
    try:
        df_zam = pd.read_csv('zamena.csv')
        df_zam.columns = [c.upper().strip() for c in df_zam.columns]
        
        for dan in dani:
            trenutni_dt = datetime.strptime(dan, '%d.%m.%Y')
            for _, zam_red in df_zam.iterrows():
                p_str = str(zam_red['DATUM POČETKA']).strip()
                z_str = str(zam_red['DATUM ZAVRŠETKA']).strip()
                
                try:
                    p_dt = datetime.strptime(p_str, '%Y-%m-%d') if '-' in p_str else datetime.strptime(p_str, '%d.%m.%Y')
                    z_dt = datetime.strptime(z_str, '%Y-%m-%d') if '-' in z_str else datetime.strptime(z_str, '%d.%m.%Y')
                    
                    # Zamena se upisuje samo ako dan upada strogo u opseg
                    if p_dt.date() <= trenutni_dt.date() <= z_dt.date():
                        m_id = str(zam_red['ID MAŠINE']).strip().upper()
                        idx_m = df_final[df_final['ID MAŠINE'] == m_id].index
                        if not idx_m.empty:
                            df_final.loc[idx_m, dan] = str(zam_red['ZAMENA']).upper().strip()
                except:
                    pass
    except:
        pass
        
    return df_final
