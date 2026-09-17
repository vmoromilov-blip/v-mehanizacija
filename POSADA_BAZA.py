import streamlit as st
import pandas as pd
import os

def prikazi_posadu(fajl_baze):
    fajl_csv = "POSADA_BAZA.csv"
    
    # Ako fajl u memoriji već postoji, obrisaćemo ga da očistimo sukobe
    if os.path.exists(fajl_csv):
        try:
            os.remove(fajl_csv)
        except:
            pass
            
    if os.path.exists(fajl_baze):
        try:
            # Čitamo originalni šit iz Excela
            df = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
            # Čistimo prazna mesta u nazivima kolona
            df.columns = [str(c).strip() for c in df.columns]
            
            # Ako kolona STATUS postoji, stavljamo AKTIVAN, ako ne - pravimo je
            df['STATUS'] = 'AKTIVAN'
            
            # Izbacujemo nepotrebne kolone ako postoje
            kolone_za_brisanje = ['EMAIL ADRESA', 'TIP', 'Unnamed: 3']
            df = df.drop(columns=[c for c in kolone_za_brisanje if c in df.columns], errors='ignore')
            
            df.to_csv(fajl_csv, index=False)
        except:
            df = pd.DataFrame(columns=['SAP BROJ', 'PREZIME I IME', 'STATUS'])
    else:
        df = pd.DataFrame(columns=['SAP BROJ', 'PREZIME I IME', 'STATUS'])

    try:
        df = pd.read_csv(fajl_csv)
    except:
        return

    # 🎯 AUTOMATSKO SORTIRANJE OD A DO Z PO DRUGOJ KOLONI (IME I PREZIME)
    if len(df.columns) > 1:
        kolona_za_sort = df.columns[1] # Uzimamo kolonu sa imenima, kako god da se tačno zove
        df = df.sort_values(by=kolona_za_sort).reset_index(drop=True)

    # Čisto fabričko dugme na samom vrhu ekrana
    with st.popover("➕ DODAJ RADNIKA"):
        st.write("### Unesi novog radnika u sistem")
        novo_ime = st.text_input("Prezime i ime radnika:")
        novi_sap = st.text_input("SAP broj radnika:")
        if st.button("SAČUVAJ U VOZAČE"):
            if novo_ime:
                kolone = list(df.columns)
                novi_red = {kolone[0]: novi_sap.strip(), kolone[1]: novo_ime.upper().strip()}
                if len(kolone) > 2:
                    novi_red[kolone[2]] = 'AKTIVAN'
                
                df = pd.concat([df, pd.DataFrame([novi_red])], ignore_index=True)
                df.to_csv(fajl_csv, index=False)
                st.success("Radnik uspešno upisan!")
                st.rerun()
                    
    st.write("")

    # Pokrećemo čistu tabelu bez ručnog kucanja parametara da ne može da pukne
    izmenjeni_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        key="zivi_editor_radnika_konacni_stopostotni"
    )
    
    if izmenjeni_df is not None and not izmenjeni_df.equals(df):
        izmenjeni_df.to_csv(fajl_csv, index=False)
        st.rerun()
