import streamlit as st
import pandas as pd
import os
from datetime import datetime

def prikazi_ispravnost(fajl_baze):
    st.write("## 🛠️ Dnevna ispravnost mehanizacije")
    
    fajl_csv = "ispravnost_baza.csv"
    trenutna_godina = datetime.now().strftime('%Y')
    danasnji_str = datetime.now().strftime('%d.%m.%Y')
    
    # Ako fajl ne postoji, ili ako je pukao i ostao potpuno prazan
    if not os.path.exists(fajl_csv) or os.path.getsize(fajl_csv) == 0:
        if os.path.exists(fajl_baze):
            df = pd.read_excel(fajl_baze, sheet_name='ISPRAVNOST')
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
        
    df = df.fillna('DA')
    
    # --- 🚀 ROBUSTNA AUTOMATIKA: DODAVANJE NOVIH MAŠINA SA PLUSIĆA (KIPER VM) ---
    fajl_zivih = 'spisak_mašina.csv' if os.path.exists('spisak_mašina.csv') else ('spisak_masina.csv' if os.path.exists('spisak_masina.csv') else '')
    if fajl_zivih != "":
        try:
            df_zive_masine = pd.read_csv(fajl_zivih)
            for _, red in df_zive_masine.iterrows():
                gb = str(red['GARAŽNI BROJ']).strip()
                tip = str(red['TIP MAŠINE']).strip()
                
                # Proveravamo da li garažni broj već postoji u kalendaru ispravnosti
                postojeci_gb = df['ID MAŠINE'].astype(str).str.strip().values
                if gb not in postojeci_gb:
                    # Pravimo novi red za novu mašinu i punimo ceo kalendar sa "DA"
                    novi_red = {'MAŠINA': tip, 'ID MAŠINE': gb}
                    for col in df.columns:
                        if col not in ['MAŠINA', 'ID MAŠINE']:
                            novi_red[col] = 'DA'
                    df = pd.concat([df, pd.DataFrame([novi_red])], ignore_index=True)
            df.to_csv(fajl_csv, index=False)
        except:
            pass
    # -------------------------------------------------------------------------

    # --- ⚙️ VRAĆAMO DUGME ZA PROJEKTOVANJE ISPRAVNOSTI DO KRAJA GODINE ---
    with st.popover("⚙️ Grupna promena (Projektuj do kraja godine)"):
        st.write("### Unesi status i prenesi ga automatski na sve naredne dane")
        izabrana_masina = st.selectbox("Izaberi mašinu (ID):", df['ID MAŠINE'].dropna().unique())
        datum_promene = st.date_input("Izaberi datum od kog projektuješ:", datetime.now().date())
        datum_promene_str = datum_promene.strftime('%d.%m.%Y')
        novi_status = st.radio("Status za projektovanje:", ["DA", "NE", "MIR", "VIK"], horizontal=True)
        
        if st.button("Sačuvaj i projektuj trajno"):
            if datum_promene_str in df.columns:
                idx = df[df['ID MAŠINE'].astype(str).str.strip() == str(izabrana_masina).strip()].index
                if not idx.empty:
                    sve_kolone = list(df.columns)
                    start_idx = sve_kolone.index(datum_promene_str)
                    # Menjamo izabrani datum i sve datume udesno do 31. decembra!
                    for c in sve_kolone[start_idx:]:
                        df.loc[idx, c] = novi_status
                    df.to_csv(fajl_csv, index=False)
                    st.success("Status uspešno i trajno projektovan do kraja godine!")
                    st.rerun()
            else:
                st.error(f"Izabrani datum {datum_promene_str} se ne nalazi u kalendaru.")
    st.write("")
    
    st.write("### 📅 Filter kalendara")
    meseci = ["Januar", "Februar", "Mart", "April", "Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar", "Novembar", "Decembar"]
    trenutni_mesec_idx = datetime.now().month - 1
    izabrani_mesec = st.selectbox("Izaberi mesec za prikaz:", meseci, index=trenutni_mesec_idx)
    
    mesec_broj_str = str(meseci.index(izabrani_mesec) + 1).zfill(2)
    ekstenzija_meseca = f".{mesec_broj_str}.{trenutna_godina}"
    
    osnovne_kolone = ['MAŠINA', 'ID MAŠINE']
    kalendarske_kolone = [c for c in df.columns if c.endswith(ekstenzija_meseca)]
    
    if danasnji_str in kalendarske_kolone:
        idx_danas = kalendarske_kolone.index(danasnji_str)
        poredjane_kolone = osnovne_kolone + kalendarske_kolone[max(0, idx_danas-2):] + kalendarske_kolone[:max(0, idx_danas-2)]
    else:
        poredjane_kolone = osnovne_kolone + kalendarske_kolone

    konfiguracija_kolona = {
        "MAŠINA": st.column_config.TextColumn("MAŠINA", pinned=True, disabled=True),
        "ID MAŠINE": st.column_config.TextColumn("ID MAŠINE", pinned=True, disabled=True)
    }
    for col in kalendarske_kolone:
        naziv_zaglavlja = f"🚨 {col} (DANAS) 🚨" if col == danasnji_str else col
        konfiguracija_kolona[col] = st.column_config.SelectboxColumn(naziv_zaglavlja, options=["DA", "NE", "MIR", "VIK"], required=True)

    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        column_order=poredjane_kolone,
        column_config=konfiguracija_kolona,
        key="editor_ispravnosti_brzi"
    )
    
    if izmenjeni_df is not None:
        osnovni_df = pd.DataFrame(izmenjeni_df.values, columns=df.columns)
        if not osnovni_df.equals(df):
            osnovni_df.to_csv(fajl_csv, index=False)
            st.rerun()
