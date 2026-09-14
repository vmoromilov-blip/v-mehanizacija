import streamlit as st
import pandas as pd
import os

# Podešavamo naslovnu stranu sajta
st.set_page_config(page_title="Operativni Izveštaji", layout="wide")

# Glavni naslov sajta
st.title("🚜 Operativni izveštaji mehanizacije")

# Pravimo bočni meni sa leve strane za module
st.sidebar.header("Meni sa modulima")
modul = st.sidebar.radio("Izaberi modul:", ["Početna", "SPISAK MAŠINA"])

if modul == "Početna":
    st.write("### Dobrodošli u operativni sistem mehanizacije!")
    st.write("Izaberite modul sa leve strane kako biste videli podatke.")
    
elif modul == "SPISAK MAŠINA":
    st.write("## 📋 Spisak mehanizacije")
    
    # 1. Proveravamo da li fajl postoji, ako ne, pravimo osnovnu tabelu
    fajl_baze = 'plan.xlsm'
    
    if os.path.exists(fajl_baze):
        df = pd.read_excel(fajl_baze, sheet_name='SPISAK MAŠINA')
    else:
        # Ako fajl nekim čudom nestane, pravimo praznu tabelu sa tvojim kolonama
        df = pd.DataFrame(columns=['TIP MAŠINE', 'GARAŽNI BROJ'])

    # 2. PRAVIMO PLUS "+" DUGME U GORNJEM LEVOM UGLU
    # Pravimo iskačući prozorčić (popover) koji glumi tvoj plus dugme
    with st.popover("➕ Dodaj novu mašinu"):
        st.write("### Unesi podatke za novu mehanizaciju")
        
        # Polja za unos teksta
        novi_tip = st.text_input("Tip mašine (npr. BAGER, BULDOZER):")
        novi_gb = st.text_input("Garažni broj (npr. GB4760):")
        
        # Dugme koje potvrđuje unos
        if st.button("Sačuvaj u sistemu"):
            if novi_tip and novi_gb:
                # Pravimo novi red i dodajemo ga u našu tabelu u memoriji
                novi_red = pd.DataFrame([{'TIP MAŠINE': novi_tip.upper(), 'GARAŽNI BROJ': novi_gb.upper()}])
                df = pd.concat([df, novi_red], ignore_index=True)
                
                # VAŽNO: Pošto je Excel fajl na serveru privremen, privremeno ga čuvamo u memoriji
                # U pravom sistemu ovde ide upis u bazu podataka (rešićemo i to čim prođe test)
                st.success(f"Uspešno dodata mašina: {novi_tip.upper()} ({novi_gb.upper()})")
                st.rerun() # Osvežavamo sajt da se odmah vidi promena u tabeli
            else:
                st.error("Morate popuniti oba polja!")

    # Razmak između dugmeta i tabele
    st.write("")
    
    # 3. Prikazujemo čistu tabelu preko celog ekrana (sa novim izmenama)
    st.dataframe(df, use_container_width=True)
