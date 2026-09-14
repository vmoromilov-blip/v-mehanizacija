import streamlit as st
import pandas as pd
import os

# Podešavamo naslovnu stranu sajta
st.set_page_config(page_title="Operativni Izveštaji", layout="wide")

# Glavni naslov sajta
st.title("🚜 Operativni izveštaji mehanizacije")

# Pravimo bočni meni sa leve strane za module - DODALI SMO SPISAK RADNIKA
st.sidebar.header("Meni sa modulima")
modul = st.sidebar.radio("Izaberi modul:", ["Početna", "SPISAK MAŠINA", "SPISAK RADNIKA"])

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

    # PLUS DUGME ZA MAŠINE
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
    
    # Čitamo šit sa radnicima iz Excela
    if os.path.exists(fajl_baze):
        df_radnici = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
    else:
        df_radnici = pd.DataFrame(columns=['IME I PREZIME', 'RADNO MESTO'])

    # PLUS DUGME ZA RADNIKE u gornjem levom uglu
    with st.popover("➕ Dodaj novog radnika"):
        st.write("### Unesi podatke za novog zaposlenog")
        novo_ime = st.text_input("Ime i prezime radnika:")
        novo_mesto = st.text_input("Radno mesto / Pozicija (npr. VOZAČ, MEHANIČAR):")
        
        if st.button("Sačuvaj radnika"):
            if novo_ime and novo_mesto:
                # Pravimo novi red za radnika (prilagodiće se tvojim pravim kolonama)
                # Ako tvoje kolone u Excelu imaju drugačije nazive, zamenićemo ih lako ovde
                novi_radnik = pd.DataFrame([{'IME I PREZIME': novo_ime.upper(), 'RADNO MESTO': novo_mesto.upper()}])
                df_radnici = pd.concat([df_radnici, novi_radnik], ignore_index=True)
                st.success(f"Uspešno dodat radnik: {novo_ime.upper()} ({novo_mesto.upper()})")
                st.rerun()
            else:
                st.error("Morate popuniti oba polja!")

    st.write("")
    # Prikazujemo tabelu sa radnicima preko celog ekrana
    st.dataframe(df_radnici, use_container_width=True)
