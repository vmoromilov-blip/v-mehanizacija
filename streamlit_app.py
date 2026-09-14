import streamlit as st
import pandas as pd

# Podešavamo naslovnu stranu sajta
st.set_page_config(page_title="Operativni Izveštaji", layout="wide")

# Glavni naslov sajta (Kao tvoj Excel!)
st.title("🚜 Operativni izveštaji mehanizacije")

# Pravimo bočni meni sa leve strane za module
st.sidebar.header("Meni sa modulima")
modul = st.sidebar.radio("Izaberi modul:", ["Početna", "SPISAK MAŠINA"])

if modul == "Početna":
    st.write("### Dobrodošli u operativni sistem mehanizacije!")
    st.write("Izaberite modul sa leve strane kako biste videli podatke.")
    
elif modul == "SPISAK MAŠINA":
    st.write("## 📋 Spisak mehanizacije")
    
    # Učitavamo podatke iz fajla koji je pored koda
    df = pd.read_excel('plan.xlsx', sheet_name='SPISAK MAŠINA')
    
    # Prikazujemo čistu tabelu preko celog ekrana
    st.dataframe(df, use_container_width=True)
