import streamlit as st
import pandas as pd
import os
from datetime import datetime

# UVOZIMO NAŠE NOVE KRUPNE PODFASCIKLE VELIKIM SLOVIMA
from GARAŽNA_BAZA import prikazi_garazu
from POSADA_BAZA import prikazi_posadu
from ZAMENA_BAZA import prikazi_zamenu
from NOSIOCI_BAZA import prikazi_nosioce
from ISPRAVNOST_EKRAN import prikazi_ispravnost
from RASPORED_EKRAN import prikazi_raspored

# Podešavamo sajt da fabrički uvek koristi maksimalnu širinu ekrana
st.set_page_config(page_title="Operativni Izveštaji", layout="wide")

st.sidebar.header("MENI SA MODULIMA")
modul = st.sidebar.radio("IZABERI MODUL:", ["POČETNA", "GARAŽA", "SPISAK VOZAČA", "ZAMENA", "NOSIOCI", "ISPRAVNOST", "RASPORED"])

fajl_baze = 'plan.xlsm'

if modul == "POČETNA":
    st.write("### Dobrodošli u operativni sistem mehanizacije!")
    st.write("Izaberite modul sa leve strane kako biste videli podatke.")
    
elif modul == "GARAŽA":
    prikazi_garazu(fajl_baze)

elif modul == "SPISAK VOZAČA":
    prikazi_posadu(fajl_baze)

elif modul == "ZAMENA":
    prikazi_zamenu(fajl_baze)

elif modul == "NOSIOCI":
    prikazi_nosioce(fajl_baze)

elif modul == "ISPRAVNOST":
    prikazi_ispravnost(fajl_baze)

elif modul == "RASPORED":
    prikazi_raspored(fajl_baze)
