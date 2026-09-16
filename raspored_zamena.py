import pandas as pd
import os
from datetime import datetime

def primeni_vojne_zamene(df_final, dani):
    fajl_zamene = "zamena.csv"
    
    if os.path.exists(fajl_zamene):
        try:
            df_zamene = pd.read_csv(fajl_zamene)
            
            for dan in dani:
                trenutni_dt = datetime.strptime(dan, '%d.%m.%Y')
                
                for _, zam_red in df_zamene.iterrows():
                    p_str = str(zam_red['DATUM POČETKA']).strip()
                    z_str = str(zam_red['DATUM ZAVRŠETKA']).strip()
                    
                    # Prepoznajemo formate datuma iz baze
                    p_dt = datetime.strptime(p_str, '%Y-%m-%d') if '-' in p_str else datetime.strptime(p_str, '%d.%m.%Y')
                    z_dt = datetime.strptime(z_str, '%Y-%m-%d') if '-' in z_str else datetime.strptime(z_str, '%d.%m.%Y')
                    
                    # Ako dan upada u opseg zamene, prebrisavamo nosioca realnim stanjem
                    if p_dt <= trenutni_dt <= z_dt:
                        m_id = str(zam_red['ID MAŠINE']).strip()
                        idx_m = df_final[df_final['ID MAŠINE'].astype(str).str.strip() == m_id].index
                        if not idx_m.empty:
                            df_final.loc[idx_m, dan] = str(zam_red['ZAMENA']).upper()
        except:
            pass
            
    return df_final
