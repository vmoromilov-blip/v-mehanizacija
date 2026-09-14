import streamlit as st
import pandas as pd
import os

# Podešavamo naslovnu stranu sajta
st.set_page_config(page_title="Operativni Izveštaji", layout="wide")

# Glavni naslov sajta
st.title("🚜 Operativni izveštaji mehanizacije")

# Bočni meni sa leve strane - DODALI SMO I ZAMENU
st.sidebar.header("Meni sa modulima")
modul = st.sidebar.radio("Izaberi modul:", ["Početna", "SPISAK MAŠINA", "SPISAK RADNIKA", "ZAMENA"])

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
        novi_tip = st.text_input("Tip mašine (npr. BAGER, BULDOZER):")
        novi_gb = st.text_input("Garažni broj (npr. GB4760):")
        if st.button("Sačuvaj mašinu"):
            if novi_tip and novi_gb:
                novi_red = pd.DataFrame([{'TIP MAŠINE': novi_tip.upper(), 'GARAŽNI BROJ': novi_gb.upper()}])
                df_masine = pd.concat([df_masine, novi_red], ignore_index=True)
                st.success(f"Uspešno dodata mašina: {novi_tip.upper()} ({novi_gb.upper()})")
                st.rerun()
            else:
                st.error("Morate popuniti oba polja!")
    st.write("")
    st.dataframe(df_masine, use_container_width=True)

elif modul == "SPISAK RADNIKA":
    st.write("## 👥 Spisak zaposlenih radnika")
    if os.path.exists(fajl_baze):
        df_radnici = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
    else:
        df_radnici = pd.DataFrame(columns=['SAP BROJ', 'PREZIME I IME', 'STATUS', 'TIP'])

    with st.popover("➕ Dodaj novog radnika"):
        st.write("### Unesi podatke za novog zaposlenog")
        novo_ime = st.text_input("Ime i prezime radnika:")
        novo_mesto = st.text_input("Radno mesto / Pozicija:")
        if st.button("Sačuvaj radnika"):
            if ...:  # Zadržavamo privremenu logiku unosa
                st.success("Radnik dodat!")
                st.rerun()

    st.write("")
    prikaz_df = df_radnici.drop(columns=['EMAIL ADRESA', 'Unnamed: 3'], errors='ignore')
    st.dataframe(prikaz_df, use_container_width=True)

# ---> NOVI MODUL: ZAMENA <---
elif modul == "ZAMENA":
    st.write("## 🔄 Spisak i evidencija zamena")
    
    # Čitamo šit sa zamenama iz Excela
    if os.path.exists(fajl_baze):
        df_zamena = pd.read_excel(fajl_baze, sheet_name='ZAMENA')
    else:
        df_zamena = pd.DataFrame(columns=['OSNOVNI RESURS', 'ZAMENA'])

    # PLUS DUGME ZA ZAMENE u gornjem levom uglu
    with st.popover("➕ Dodaj novu zamenu"):
        st.write("### Unesi podatke za novu zamenu")
        osnovno = st.text_input("Šta/Ko se menja (npr. Mašina ili Radnik):")
        zamenski = st.text_input("Šta/Ko je zamena:")
        
        if st.button("Sačuvaj zamenu"):
            if osnovno and zamenski:
                st.success(f"Uspešno uneta zamena u sistem!")
                st.rerun()
            else:
                st.error("Morate popuniti oba polja!")

    st.write("")
    # Prikazujemo tabelu sa zamenama preko celog ekrana
    st.dataframe(df_zamena, use_container_width=True)
