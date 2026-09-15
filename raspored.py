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
    
    # Ako baza u fascikli još ne postoji, pravimo je inicijalno iz Excela
    if not os.path.exists(fajl_csv) or os.path.getsize(fajl_csv) == 0:
        if os.path.exists(fajl_baze):
            df = pd.read_excel(fajl_baze, sheet_name='RASPORED')
            df = df.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
            df.columns = [col.strftime('%d.%m.%Y') if isinstance(col, datetime) else str(col) for col in df.columns]
            
            # --- VOJNIČKA AUTOMATIKA PRI PRVOM POKRETANJU ---
            # Za svaku kolonu (datum) u kalendaru računamo turnus i proveravamo zamene
            for col in df.columns:
                if col not in ['MAŠINA', 'ID MAŠINE']:
                    # 1. Povlačimo dežurnog nosioca po turnusu (radi-ladi) za taj konkretan dan
                    nosioci_za_dan = izracunaj_aktivnog_nosioca(fajl_baze, col)
                    
                    for idx, red in df.iterrows():
                        masina_id = str(red['ID MAŠINE']).strip()
                        # Postavljamo osnovnog nosioca iz turnusa
                        if masina_id in nosioci_za_dan:
                            df.at[idx, col] = nosioci_za_dan[masina_id]
                            
                    # 2. Proveravamo da li za ovaj datum postoji "izričita naredba" u ZAMENAMA
                    if os.path.exists('zamena.csv'):
                        df_zamene = pd.read_csv('zamena.csv')
                        try:
                            # Pretvaramo datume u zameni u čist tekst radi poređenja
                            df_zamene['DATUM POČETKA'] = pd.to_datetime(df_zamene['DATUM POČETKA']).dt.strftime('%d.%m.%Y')
                            df_zamene['DATUM ZAVRŠETKA'] = pd.to_datetime(df_zamena['DATUM ZAVRŠETKA']).dt.strftime('%d.%m.%Y')
                            
                            trenutni_dt = datetime.strptime(col, '%d.%m.%Y')
                            
                            for _, zam_red in df_zamene.iterrows():
                                p_dt = datetime.strptime(zam_red['DATUM POČETKA'], '%d.%m.%Y')
                                z_dt = datetime.strptime(zam_red['DATUM ZAVRŠETKA'], '%d.%m.%Y')
                                
                                # Ako dan upada u vojnički opseg zamene, prebrisavamo nosioca realnim stanjem!
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
                # Nova mašina dobija nosioca na osnovu turnusa za sve dane
                for col in df.columns:
                    if col not in ['MAŠINA', 'ID MAŠINE']:
                        nosioci_za_dan = izracunaj_aktivnog_nosioca(fajl_baze, col)
                        novi_red[col] = nosioci_za_dan.get(gb, '')
                df = pd.concat([df, pd.DataFrame([novi_red])], ignore_index=True)
        df.to_csv(fajl_csv, index=False)

    # Učitavamo spisak radnika za padajući meni na dvoklik
    opcije_radnika = [""]
    if os.path.exists('spisak_radnika.csv'):
        try:
            df_radnici_baza = pd.read_csv('spisak_radnika.csv')
            if 'PREZIME I IME' in df_radnici_baza.columns:
                opcije_radnika.extend(sorted(df_radnici_baza['PREZIME I IME'].dropna().astype(str).unique()))
        except:
            pass

    st.write("")
    
    # --- FIKSIRANJE CELOG KALENDARA I AUTOMATSKI SKOK NA DANAS ---
    sve_kolone = list(df.columns)
    osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
    kalendarske_kolone = [c for c in sve_kolone if c not in osnovne_kolone]
    
    if danasnji_str in kalendarske_kolone:
        idx_danas = kalendarske_kolone.index(danasnji_str)
        poredjane_kolone = osnovne_kolone + kalendarske_kolone[max(0, idx_danas-2):] + kalendarske_kolone[:max(0, idx_danas-2)]
    else:
        poredjane_kolone = sve_kolone

    # --- KONFIGURACIJA TABELE SA PADAJUĆIM MENIJIMA RADNIKA ---
    konfiguracija_kolona = {
        "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True, disabled=True),
        "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True, disabled=True)
    }
    
    for col in poredjane_kolone:
        if col not in ["MAŠINA", "ID MAŠINE"]:
            if len(opcije_radnika) > 1:
                konfiguracija_kolona[col] = st.column_config.SelectboxColumn(
                    f"🚨 {col} (DANAS) 🚨" if col == danasnji_str else col,
                    options=opcije_radnika
                )
            else:
                konfiguracija_kolona[col] = st.column_config.TextColumn(f"🚨 {col} (DANAS) 🚨" if col == danasnji_str else col)

    # Pokrećemo čisti data_editor za Raspored centriran na danasnji dan
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        column_order=poredjane_kolone,
        column_config=konfiguracija_kolona,
        key="zivi_editor_rasporeda"
    )
    
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
