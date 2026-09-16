import streamlit as st
import pandas as pd
import os
from datetime import datetime
from nosioci import izracunaj_aktivnog_nosioca

def prikazi_raspored(fajl_baze):
    st.write("## 📅 Kalendarski raspored mehanizacije i vozača")
    
    fajl_csv = "raspored_baza.csv"
    danasnji_str = datetime.now().strftime('%d.%m.%Y')
    trenutna_godina = datetime.now().strftime('%Y')

    # 1. Čitamo bazu ili je pravimo inicijalno bez ikakvog teškog računanja cele godine
    if not os.path.exists(fajl_csv) or os.path.getsize(fajl_csv) == 0:
        if os.path.exists(fajl_baze):
            df = pd.read_excel(fajl_baze, sheet_name='RASPORED')
            df = df.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
            df.columns = [col.strftime('%d.%m.%Y') if isinstance(col, datetime) else str(col) for col in df.columns]
            df.to_csv(fajl_csv, index=False)
        else:
            st.error("Glavni Excel fajl 'plan.xlsm' nije pronađen.")
            return

    try:
        df = pd.read_csv(fajl_csv)
    except:
        return
        
    df = df.fillna('')
    
    # --- MESEČNI FILTER (OVO SPASAVA SERVED OD MOTANJA!) ---
    st.write("### 📅 Filter kalendara")
    meseci = ["Januar", "Februar", "Mart", "April", "Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar", "Novembar", "Decembar"]
    trenutni_mesec_idx = datetime.now().month - 1
    izabrani_mesec = st.selectbox("Izaberi mesec za prikaz:", meseci, index=trenutni_mesec_idx, key="filter_brzog_rasporeda")
    
    mesec_broj_str = str(meseci.index(izabrani_mesec) + 1).zfill(2)
    ekstenzija_meseca = f".{mesec_broj_str}.{trenutna_godina}"
    
    osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
    kalendarske_kolone = [c for c in df.columns if c.endswith(ekstenzija_meseca)]
    
    # 2. 🧮 VOJNIČKA LOGIKA SPAJANJA SE IZVRŠAVA SAMO ZA DANAS I IZABRANI MESEC!
    for col in kalendarske_kolone:
        # KORAK 1: Nosioci iz turnusa
        nosioci_za_dan = izracunaj_aktivnog_nosioca(fajl_baze, col)
        for idx, red in df.iterrows():
            m_id = str(red['ID MAŠINE']).strip()
            if m_id in nosioci_za_dan:
                df.at[idx, col] = nosioci_za_dan[m_id]
                
        # KORAK 2: Oduzimanje na osnovu Ispravnosti (NE, MIR, VIK ostaju prazni)
        if os.path.exists('ispravnost_baza.csv'):
            try:
                df_isp = pd.read_csv('ispravnost_baza.csv')
                if col in df_isp.columns:
                    for idx, red in df.iterrows():
                        m_id = str(red['ID MAŠINE']).strip()
                        status_red = df_isp[df_isp['ID MAŠINE'].astype(str).str.strip() == m_id]
                        if not status_red.empty:
                            trenutni_status = str(status_red[col].values[0]).strip().upper() if len(status_red[col].values) > 0 else ""
                            if 'NE' in trenutni_status or 'MIR' in trenutni_status or 'VIK' in trenutni_status:
                                df.at[idx, col] = ''
            except:
                pass

        # KORAK 3: Vojna naredba iz Zamena
        if os.path.exists('zamena.csv'):
            try:
                df_zamene = pd.read_csv('zamena.csv')
                trenutni_dt = datetime.strptime(col, '%d.%m.%Y')
                for _, zam_red in df_zamene.iterrows():
                    p_str = str(zam_red['DATUM POČETKA']).strip()
                    z_str = str(zam_red['DATUM ZAVRŠETKA']).strip()
                    p_dt = datetime.strptime(p_str, '%Y-%m-%d') if '-' in p_str else datetime.strptime(p_str, '%d.%m.%Y')
                    z_dt = datetime.strptime(z_str, '%Y-%m-%d') if '-' in z_str else datetime.strptime(z_str, '%d.%m.%Y')
                    
                    if p_dt <= trenutni_dt <= z_dt:
                        m_id = str(zam_red['ID MAŠINE']).strip()
                        idx_m = df[df['ID MAŠINE'].astype(str).str.strip() == m_id].index
                        if not idx_m.empty:
                            df.loc[idx_m, col] = str(zam_red['ZAMENA']).upper()
            except:
                pass

    # Dodavanje novih mašina sa plusića na dno tabele
    fajl_zivih_masine = 'spisak_mašina.csv' if os.path.exists('spisak_mašina.csv') else ('spisak_masina.csv' if os.path.exists('spisak_masina.csv') else '')
    if fajl_zivih_masine != "":
        try:
            df_zive_masine = pd.read_csv(fajl_zivih_masine)
            for _, red in df_zive_masine.iterrows():
                gb = str(red['GARAŽNI BROJ']).strip()
                tip = str(red['TIP MAŠINE']).strip()
                if gb not in df['ID MAŠINE'].astype(str).str.strip().values:
                    novi_red = {'MAŠINA': tip, 'ID MAŠINE': gb}
                    for col in df.columns:
                        if col not in ['MAŠINA', 'ID MAŠINE']:
                            novi_red[col] = ''
                    df = pd.concat([df, pd.DataFrame([novi_red])], ignore_index=True)
        except:
            pass

    # Centriranje ekrana na današnji dan unutar tekućeg meseca
    if danasnji_str in kalendarske_kolone:
        idx = kalendarske_kolone.index(danasnji_str)
        poredjane_kolone = osnovne_kolone + kalendarske_kolone[max(0, idx-2):] + kalendarske_kolone[:max(0, idx-2)]
    else:
        poredjane_kolone = osnovne_kolone + kalendarske_kolone

    opcije_radnika = [""]
    if os.path.exists('spisak_radnika.csv'):
        try:
            df_radnici_baza = pd.read_csv('spisak_radnika.csv')
            opcije_radnika.extend(sorted(df_radnici_baza['PREZIME I IME'].dropna().astype(str).unique()))
        except:
            pass

    konfiguracija_kolona = {
        "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True, disabled=True),
        "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True, disabled=True)
    }
    for col in kalendarske_kolone:
        naziv_zaglavlja = f"🚨 {col} (DANAS) 🚨" if col == danasnji_str else col
        konfiguracija_kolona[col] = st.column_config.SelectboxColumn(naziv_zaglavlja, options=opcije_radnika)

    # Pokrećemo brzi data_editor sa mesečnim proračunom
    st.data_editor(
        df,
        use_container_width=True,
        column_order=poredjane_kolone,
        column_config=konfiguracija_kolona,
        key="editor_rasporeda_brzi_final"
    )
