import streamlit as st
import pandas as pd
import os

# Podešavamo naslovnu stranu sajta
st.set_page_config(page_title="Operativni Izveštaji", layout="wide")

# Glavni naslov sajta
st.title("🚜 Operativni izveštaji mehanizacije")

# Bočni meni sa leve strane
st.sidebar.header("Meni sa modulima")
modul = st.sidebar.radio("Izaberi modul:", ["Početna", "SPISAK MAŠINA", "SPISAK RADNIKA", "ZAMENA", "PRIMALAC MAIL-A", "NOSIOCI"])

fajl_baze = 'plan.xlsm'

if modul == "Početna":
    st.write("### Dobrodošli u operativni sistem mehanizacije!")
    st.write("Izaberite modul sa leve strane kako biste videli podatke.")
    
elif modul == "SPISAK MAŠINA":
    st.write("## 📋 Spisak mehanizacije")
    if os.path.exists(fajl_baze):
        df_masine = pd.read_excel(fajl_baze, sheet_name='SPISAK MAŠINA')
    else:
        df_masine = pd.DataFrame(columns=['TIP MAŠINE', 'GARAŽNI BROJ'])

    with st.popover("➕ Dodaj novu mašinu"):
        st.write("### Unesi podatke za novu mehanizaciju")
        novi_tip = st.text_input("Tip mašine:")
        novi_gb = st.text_input("Garažni broj:")
        if st.button("Sačuvaj mašinu"):
            st.success("Mašina ubačena!")
            st.rerun()
    st.write("")
    st.dataframe(df_masine, use_container_width=True)

elif modul == "SPISAK RADNIKA":
    st.write("## 👥 Spisak zaposlenih radnika")
    if os.path.exists(fajl_baze):
        df_radnici = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
    else:
        df_radnici = pd.DataFrame(columns=['SAP BROJ', 'PREZIME I IME', 'STATUS'])

    with st.popover("➕ Dodaj novog radnika"):
        st.write("### Unesi podatke za novog zaposlenog")
        novo_ime = st.text_input("Ime i prezime radnika:")
        if st.button("Sačuvaj radnika"):
            st.success("Radnik ubačen!")
            st.rerun()
    st.write("")
    prikaz_df = df_radnici.drop(columns=['EMAIL ADRESA', 'TIP', 'Unnamed: 3'], errors='ignore')
    st.dataframe(prikaz_df, use_container_width=True)

elif modul == "ZAMENA":
    st.write("## 🔄 Spisak i evidencija zamena")
    if os.path.exists(fajl_baze):
        df_zamena = pd.read_excel(fajl_baze, sheet_name='ZAMENA')
        prevod_kolona = {'START DATUM': 'DATUM POČETKA', 'END DATUM': 'DATUM ZAVRŠETKA'}
        df_zamena = df_zamena.rename(columns=prevod_kolona)
        if 'DATUM POČETKA' in df_zamena.columns:
            df_zamena['DATUM POČETKA'] = pd.to_datetime(df_zamena['DATUM POČETKA']).dt.date
        if 'DATUM ZAVRŠETKA' in df_zamena.columns:
            df_zamena['DATUM ZAVRŠETKA'] = pd.to_datetime(df_zamena['DATUM ZAVRŠETKA']).dt.date
    else:
        df_zamena = pd.DataFrame(columns=['ID MAŠINE', 'SMENA', 'ODSUTAN RADNIK', 'DATUM POČETKA', 'DATUM ZAVRŠETKA', 'ZAMENA'])

    with st.popover("➕ Dodaj novu zamenu"):
        st.write("### Unesi podatke za novu zamenu")
        osnovno = st.text_input("Šta/Ko se menja:")
        zamenski = st.text_input("Šta/Ko je zamena:")
        if st.button("Sačuvaj zamenu"):
            st.success("Zamena uneta!")
            st.rerun()
    st.write("")
    st.dataframe(df_zamena, use_container_width=True)

elif modul == "PRIMALAC MAIL-A":
    st.write("## 📧 Ljudi kojima se šalje izveštaj")
    if os.path.exists(fajl_baze):
        df_radnici = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
        if 'EMAIL ADRESA' in df_radnici.columns:
            df_mail = df_radnici[df_radnici['EMAIL ADRESA'].notna() & (df_radnici['EMAIL ADRESA'] != '')]
            with st.popover("➕ Dodaj email za izveštaj"):
                st.write("### Unesi novog primaoca izveštaja")
                novi_email = st.text_input("Email adresa:")
                tip_slanja = st.selectbox("Izaberi tip slanja:", ["TO", "CC"])
                if st.button("Sačuvaj email"):
                    st.success("Email dodat!")
                    st.rerun()
            st.write("")
            kolone_za_prikaz = [col for col in ['EMAIL ADRESA', 'TIP'] if col in df_mail.columns]
            st.dataframe(df_mail[kolone_za_prikaz], use_container_width=True)
        else:
            st.warning("Kolona 'EMAIL ADRESA' nije pronađena u šitu.")
    else:
        st.error("Fajl sa podacima nije dostupan.")

elif modul == "NOSIOCI":
    st.write("## 🔑 Zaduženja mehanizacije - Nosioci")
    if os.path.exists(fajl_baze):
        df_nosioci = pd.read_excel(fajl_baze, sheet_name='NOSIOCI')
        
        # 1. Izbacujemo kolonu TIP jer je nepotrebna
        df_nosioci = df_nosioci.drop(columns=['TIP'], errors='ignore')
        
        # 2. Prevodimo engleski naziv u srpski
        df_nosioci = df_nosioci.rename(columns={'START DATUM': 'DATUM POČETKA'})
        
        # 3. Čistimo sate i nule iz datuma
        if 'DATUM POČETKA' in df_nosioci.columns:
            df_nosioci['DATUM POČETKA'] = pd.to_datetime(df_nosioci['DATUM POČETKA']).dt.date
    else:
        df_nosioci = pd.DataFrame(columns=['ID MAŠINE', 'TIP TURNUSA', 'DATUM POČETKA', 'SMENA', 'SAP BROJ', 'NOSILAC'])

    with st.popover("➕ Dodaj novog nosioca"):
        st.write("### Unesi podatke o zaduženju")
        radnik_unos = st.text_input("Prezime i ime radnika:")
        gb_unos = st.text_input("Garažni broj mašine:")
        if st.button("Sačuvaj zaduženje"):
            st.success("Zaduženje uneto!")
            st.rerun()
            
    st.write("")
    st.dataframe(df_nosioci, use_container_width=True)
