import streamlit as st
import pandas as pd
import os
from datetime import datetime

def prikazi_raspored(fajl_baze):
    st.write("## 📅 Kalendarski raspored mehanizacije i vozača")
    
    fajl_csv = "raspored_baza.csv"
    
    # Ako fajl baze u fascikli još ne postoji, pravimo ga inicijalno iz Excela
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
        df = pd.read_excel(fajl_baze, sheet_name='RASPORED')
        df = df.rename(columns={'MAŠINA / DATUM': 'MAŠINA'})
        df.columns = [col.strftime('%d.%m.%Y') if isinstance(col, datetime) else str(col) for col in df.columns]
        df.to_csv(fajl_csv, index=False)
        df = pd.read_csv(fajl_csv)
        
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
                        novi_red[col] = ''
                df = pd.concat([df, pd.DataFrame([novi_red])], ignore_index=True)
        df.to_csv(fajl_csv, index=False)
    # ----------------------------------------------------

    danasnji_str = datetime.now().strftime('%d.%m.%Y')
    
    # Učitavamo živu listu radnika iz fascikle da bismo napravili padajući meni sa imenima
    opcije_radnika = [""]
    if os.path.exists('spisak_radnika.csv'):
        try:
            df_radnici_baza = pd.read_csv('spisak_radnika.csv')
            if 'PREZIME I IME' in df_radnici_baza.columns:
                imena = sorted(df_radnici_baza['PREZIME I IME'].dropna().astype(str).unique())
                opcije_radnika.extend(imena)
        except:
            pass

    # Popover za grupni prenos vozača na više dana ako zatreba
    with st.popover("⚙️ Grupna promena (Prenos na više dana)"):
        st.write("### Rasporedi radnika do kraja godine")
        izabrana_masina = st.selectbox("Izaberi mašinu (ID):", df['ID MAŠINE'].dropna().unique(), key="grupno_masina")
        if len(opcije_radnika) > 1:
            novi_radnik = st.selectbox("Izaberi radnika:", opcije_radnika, key="grupno_radnik")
        else:
            novi_radnik = st.text_input("Unesi prezime i ime radnika:", key="grupno_radnik_txt")
            
        datum_promene = st.date_input("Izaberi datum od kog prenosiš:", datetime.now().date(), key="grupno_datum")
        datum_promene_str = datum_promene.strftime('%d.%m.%Y')
        
        if st.button("Sačuvaj i rasporedi do kraja godine"):
            if datum_promene_str in df.columns and novi_radnik:
                idx = df[df['ID MAŠINE'].astype(str).str.strip() == str(izabrana_masina).strip()].index
                if not idx.empty:
                    sve_kolone = list(df.columns)
                    start_idx = sve_kolone.index(datum_promene_str)
                    for c in sve_kolone[start_idx:]:
                        df.loc[idx, c] = novi_radnik.upper()
                    df.to_csv(fajl_csv, index=False)
                    st.success("Radnik uspešno raspoređen do kraja godine!")
                    st.rerun()
    st.write("")
    
    # --- FIKSIRANJE CELOG KALENDARA I AUTOMATSKI SKOK NA DANAS ---
    sve_kolone = list(df.columns)
    osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
    kalendarske_kolone = [c for c in sve_kolone if c not in osnovne_kolone]
    
    if danasnji_str in kalendarske_kolone:
        idx_danas = kalendarske_kolone.index(danasnji_str)
        # Centriramo tako da se odmah vidi danas i dani nakon njega, a istorija ide na kraj desno na klizač unazad
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
            # Ako imamo živu listu radnika, pretvaramo ćelije u padajuće menije sa imenima!
            if len(opcije_radnika) > 1:
                if col == danasnji_str:
                    konfiguracija_kolona[col] = st.column_config.SelectboxColumn(
                        f"🚨 {col} (DANAS) 🚨",
                        options=opcije_radnika
                    )
                else:
                    konfiguracija_kolona[col] = st.column_config.SelectboxColumn(
                        col,
                        options=opcije_radnika
                    )
            else:
                # Ako nema radnika u bazi, ostavljamo običan tekstualni unos
                if col == danasnji_str:
                    konfiguracija_kolona[col] = st.column_config.TextColumn(f"🚨 {col} (DANAS) 🚨")
                else:
                    konfiguracija_kolona[col] = st.column_config.TextColumn(col)

    # Pokrećemo čisti data_editor za Raspored centriran na danasnji dan
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        column_order=poredjane_kolone,
        column_config=konfiguracija_kolona,
        key="zivi_editor_rasporeda"
    )
    
    # Živi upis rasporeda direktno u pozadinsku fasciklu čim se izabere ime vozača
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
