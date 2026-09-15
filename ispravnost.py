import streamlit as st
import pandas as pd
import os
from datetime import datetime

def prikazi_ispravnost(fajl_baze):
    st.write("## 🛠️ Dnevna ispravnost mehanizacije")
    
    fajl_csv = "ispravnost_baza.csv"
    
    if not os.path.exists(fajl_csv) and os.path.exists(fajl_baze):
        df = pd.read_excel(fajl_baze, sheet_name='ISPRAVNOST')
        df = df.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
        df.columns = [col.strftime('%d.%m.%Y') if isinstance(col, datetime) else str(col) for col in df.columns]
        df.to_csv(fajl_csv, index=False)
    
    if os.path.exists(fajl_csv):
        df = pd.read_csv(fajl_csv)
        df = df.fillna('DA')
        
        # --- AUTOMATSKO DODAVANJE NOVIH MAŠINA SA PLUSIĆA ---
        if os.path.exists('spisak_mašina.csv'):
            df_zive_masine = pd.read_csv('spisak_mašina.csv')
            for _, red in df_zive_masine.iterrows():
                gb = str(red['GARAŽNI BROJ']).strip()
                tip = str(red['TIP MAŠINE']).strip()
                
                postojeci_gb = df['ID MAŠINE'].astype(str).str.strip().values
                if gb not in postojeci_gb:
                    novi_red = {'MAŠINA': tip, 'ID MAŠINE': gb}
                    for col in df.columns:
                        if col not in ['MAŠINA', 'ID MAŠINE']:
                            novi_red[col] = 'DA'
                    df = pd.concat([df, pd.DataFrame([novi_red])], ignore_index=True)
            df.to_csv(fajl_csv, index=False)
        # ----------------------------------------------------

        danasnji_str = datetime.now().strftime('%d.%m.%Y')
        
        with st.popover("⚙️ Promeni status mašine"):
            st.write("### Unesi promenu statusa u kalendar")
            izabrana_masina = st.selectbox("Izaberi mašinu (ID):", df['ID MAŠINE'].dropna().unique())
            datum_promene = st.date_input("Izaberi datum za izmenu:", datetime.now().date())
            datum_promene_str = datum_promene.strftime('%d.%m.%Y')
            novi_status = st.radio("Novi status:", ["DA", "NE", "MIR", "VIK"], horizontal=True)
            prenesi_dalje = st.checkbox("Prenesi ovaj status na sve naredne dane u godini", value=True)
            
            if st.button("Sačuvaj promenu trajno"):
                if datum_promene_str in df.columns:
                    idx = df[df['ID MAŠINE'].astype(str).str.strip() == str(izabrana_masina).strip()].index
                    if not idx.empty:
                        if prenesi_dalje:
                            sve_kolone = list(df.columns)
                            start_idx = sve_kolone.index(datum_promene_str)
                            for c in sve_kolone[start_idx:]:
                                df.loc[idx, c] = novi_status
                        else:
                            df.loc[idx, datum_promene_str] = novi_status
                        
                        df.to_csv(fajl_csv, index=False)
                        st.success(f"Status trajno zabeležen u fascikli kalendara!")
                        st.rerun()
                else:
                    st.error(f"Izabrani datum {datum_promene_str} se ne nalazi u kalendaru.")
        st.write("")
        
        def oboji_status(val):
            if val == 'NE': return 'background-color: #ffcccc; color: black; font-weight: bold;'
            elif val == 'MIR': return 'background-color: #fff2cc; color: black;'
            elif val == 'VIK': return 'background-color: #d9ead3; color: black;'
            elif val == 'DA': return 'background-color: #ffffff; color: green;'
            return ''
        
        # Osenčićemo blago današnju kolonu u tabeli da se lakše uoči, ali BEZ boldovanja teksta unutar ćelija
        def osenci_danasnji_dan(s):
            if s.name == danasnji_str:
                return ['background-color: #f2f7ff; border-left: 1px solid #adcaff; border-right: 1px solid #adcaff;'] * len(s)
            return [''] * len(s)
            
        styled_df = df.style.map(oboji_status).apply(osenci_danasnji_dan, axis=0)
        
        # VRATILI SMO SVE KOLONE (VRAĆEN KLIZAČ ULEVO I UDESNO ZA CELU GODINU!)
        prikazane_kolone = list(df.columns)
        
        # Formiramo konfiguraciju gde BOLDUJEMO samo naslov današnjeg datuma u zaglavlju (gornja linija)
        konfiguracija_kolona = {
            "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True),
            "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True)
        }
        
        # Ako je današnji dan u tabeli, stavljamo mu velika masna slova u naslovu i zvezdice
        if danasnji_str in prikazane_kolone:
            konfiguracija_kolona[danasnji_str] = st.column_config.TextColumn(f"🚨 {danasnji_str} (DANAS) 🚨")

        st.dataframe(
            styled_df,
            use_container_width=True,
            column_order=prikazane_kolone,
            column_config=konfiguracija_kolona
        )
    else:
        st.error("Baza podataka nije dostupna.")
