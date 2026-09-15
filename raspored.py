import streamlit as st
import pandas as pd
import os
from datetime import datetime

# UVOZIMO NAŠ MATEMATIČKI MOTOR ZA TURNUSE
from nosioci import izracunaj_aktivnog_nosioca

def prikazi_raspored(fajl_baze):
    st.write("## 📅 Kalendarski raspored mehanizacije i vozača")
    
    fajl_csv = "raspored_baza.csv"
    danasnji_str = datetime.now().strftime('%d.%m.%Y')
    
    # --- PRISILNO ČIŠĆENJE AKO JE PRETHODNA BAZA POVUKLA POGREŠNE STATUSNA SLOVA (DA/NE/MIR) ---
    if os.path.exists(fajl_csv):
        try:
            df_provera = pd.read_csv(fajl_csv)
            # Ako u proveri nađemo previše reči 'DA' tamo gde treba da budu imena, brišemo fajl da ga sistem ponovo izgradi tačno
            if 'DA' in df_provera.values:
                os.remove(fajl_csv)
        except:
            pass

    # Ako baza u fascikli ne postoji, pravimo je inicijalno i punimo tačnim imenima
    if not os.path.exists(fajl_csv) or os.path.getsize(fajl_csv) == 0:
        if os.path.exists(fajl_baze):
            df = pd.read_excel(fajl_baze, sheet_name='RASPORED')
            df = df.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
            df.columns = [col.strftime('%d.%m.%Y') if isinstance(col, datetime) else str(col) for col in df.columns]
            
            # 1. Prvo punimo tabelu osnovnim nosiocima (IMENIMA) iz turnusa
            for col in df.columns:
                if col not in ['MAŠINA', 'ID MAŠINE']:
                    nosioci_za_dan = izracunaj_aktivnog_nosioca(fajl_baze, col)
                    for idx, red in df.iterrows():
                        masina_id = str(red['ID MAŠINE']).strip()
                        if masina_id in nosioci_za_dan:
                            df.at[idx, col] = nosioci_za_dan[masina_id]
                            
            # 2. Prebrisavamo nosioce izričitim naredbama iz ZAMENA (IMENIMA)
            if os.path.exists('zamena.csv'):
                try:
                    df_zamene = pd.read_csv('zamena.csv')
                    df_zamene['DATUM POČETKA'] = pd.to_datetime(df_zamene['DATUM POČETKA']).dt.strftime('%d.%m.%Y')
                    df_zamene['DATUM ZAVRŠETKA'] = pd.to_datetime(df_zamene['DATUM ZAVRŠETKA']).dt.strftime('%d.%m.%Y')
                    
                    for col in df.columns:
                        if col not in ['MAŠINA', 'ID MAŠINE']:
                            trenutni_dt = datetime.strptime(col, '%d.%m.%Y')
                            for _, zam_red in df_zamene.iterrows():
                                p_dt = datetime.strptime(zam_red['DATUM POČETKA'], '%d.%m.%Y')
                                z_dt = datetime.strptime(zam_red['DATUM ZAVRŠETKA'], '%d.%m.%Y')
                                
                                if p_dt <= trenutni_dt <= z_dt:
                                    m_id = str(zam_red['ID MAŠINE']).strip()
                                    idx_m = df[df['ID MAŠINE'].astype(str).str.strip() == m_id].index
                                    if not idx_m.empty:
                                        df.loc[idx_m, col] = str(zam_red['ZAMENA']).upper()
                except:
                    pass
            df.to_csv(fajl_csv, index=False)
        else:
            st.error("Glavni Excel fajl 'plan.xlsm' nije pronađen.")
            return

    try:
        df = pd.read_csv(fajl_csv)
    except:
        df = pd.DataFrame(columns=['MAŠINA', 'ID MAŠINE', danasnji_str])
        
    df = df.fillna('')
    
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
                        nosioci_za_dan = izracunaj_aktivnog_nosioca(fajl_baze, col)
                        novi_red[col] = nosioci_za_dan.get(gb, '')
                df = pd.concat([df, pd.DataFrame([novi_red])], ignore_index=True)
        df.to_csv(fajl_csv, index=False)

    # --- 🧮 POPRAVLJENA LOGIKA AUTOMATSKOG PRAŽNJENJA ĆELIJA NA OSNOVU ISPRAVNOSTI ---
    if os.path.exists('ispravnost_baza.csv'):
        try:
            df_isp = pd.read_csv('ispravnost_baza.csv')
            df_isp['ID MAŠINE'] = df_isp['ID MAŠINE'].astype(str).str.strip()
            
            for col in df.columns:
                if col not in ['MAŠINA', 'ID MAŠINE'] and col in df_isp.columns:
                    for idx, red in df.iterrows():
                        m_id = str(red['ID MAŠINE']).strip()
                        status_red = df_isp[df_isp['ID MAŠINE'] == m_id]
                        if not status_red.empty:
                            # HIRURŠKI PRECIZNO: Čitamo samo vrednost iz te ćelije
                            trenutni_status = str(status_red[col].values[0]).strip().upper()
                            # Ako mašina ima kvar, mirovanje ili je vikend, brišemo vozača iz rasporeda da polje ostane PRAZNO
                            if trenutni_status in ['NE', 'MIR', 'VIK']:
                                df.at[idx, col] = ''
        except:
            pass

    # Učitavamo spisak radnika za padajući meni
    opcije_radnika = [""]
    if os.path.exists('spisak_radnika.csv'):
        try:
            df_radnici_baza = pd.read_csv('spisak_radnika.csv')
            if 'PREZIME I IME' in df_radnici_baza.columns:
                opcije_radnika.extend(sorted(df_radnici_baza['PREZIME I IME'].dropna().astype(str).unique()))
        except:
            pass

    prikazane_kolone = list(df.columns)

    # --- KONFIGURACIJA TABELE SA PADAJUĆIM MENIJIMA ---
    konfiguracija_kolona = {
        "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True, disabled=True),
        "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True, disabled=True)
    }
    
    for col in prikazane_kolone:
        if col not in ["MAŠINA", "ID MAŠINE"]:
            if len(opcije_radnika) > 1:
                konfiguracija_kolona[col] = st.column_config.SelectboxColumn(
                    f"🚨 {col} (DANAS) 🚨" if col == danasnji_str else col,
                    options=opcije_radnika
                )
            else:
                konfiguracija_kolona[col] = st.column_config.TextColumn(f"🚨 {col} (DANAS) 🚨" if col == danasnji_str else col)

    # Pokrećemo čisti data_editor za Raspored od 1. januara sa kompletnim klizačem
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        column_order=prikazane_kolone,
        column_config=konfiguracija_kolona,
        key="zivi_editor_rasporeda"
    )
    
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
