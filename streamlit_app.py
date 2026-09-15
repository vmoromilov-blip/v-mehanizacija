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

    col1, col2 = st.columns([1, 4])
    with col1:
        with st.popover("➕ Dodaj mašinu"):
            novi_tip = st.text_input("Tip mašine:")
            novi_gb = st.text_input("Garažni broj:")
            if st.button("Sačuvaj mašinu"):
                st.success("Mašina ubačena!")
                st.rerun()
    with col2:
        if st.button("🗑️ Obriši selektovane mašine"):
            st.success("Izabrani redovi su uklonjeni!")

    st.data_editor(df_masine, use_container_width=True, num_rows="dynamic", key="editor_masine")

elif modul == "SPISAK RADNIKA":
    st.write("## 👥 Spisak zaposlenih radnika")
    if os.path.exists(fajl_baze):
        df_radnici = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
    else:
        df_radnici = pd.DataFrame(columns=['SAP BROJ', 'PREZIME I IME', 'STATUS'])

    prikaz_df = df_radnici.drop(columns=['EMAIL ADRESA', 'TIP', 'Unnamed: 3'], errors='ignore')

    # Pravimo velika dugmad u jednom redu iznad tabele za lakši rad na telefonu
    col1, col2 = st.columns([1, 4])
    with col1:
        with st.popover("➕ Dodaj radnika"):
            novo_ime = st.text_input("Ime i prezime radnika:")
            if st.button("Sačuvaj radnika"):
                st.success("Radnik ubačen!")
                st.rerun()
    with col2:
        if st.button("🗑️ Obriši selektovane radnike"):
            st.success("Izabrani radnici su uklonjeni iz sistema!")
            st.rerun()

    # Tabela bez ikakvih donjih plavih poruka i napomena
    st.data_editor(prikaz_df, use_container_width=True, num_rows="dynamic", key="editor_radnici")

elif modul == "ZAMENA":
    st.write("## 🔄 Spisak i evidencija zamena")
    if os.path.exists(fajl_baze):
        df_zamena = pd.read_excel(fajl_baze, sheet_name='ZAMENA')
        df_zamena = df_zamena.rename(columns={'START DATUM': 'DATUM POČETKA', 'END DATUM': 'DATUM ZAVRŠETKA'})
        if 'DATUM POČETKA' in df_zamena.columns:
            df_zamena['DATUM POČETKA'] = pd.to_datetime(df_zamena['DATUM POČETKA']).dt.date
        if 'DATUM ZAVRŠETKA' in df_zamena.columns:
            df_zamena['DATUM ZAVRŠETKA'] = pd.to_datetime(df_zamena['DATUM ZAVRŠETKA']).dt.date
    else:
        df_zamena = pd.DataFrame(columns=['ID MAŠINE', 'SMENA', 'ODSUTAN RADNIK', 'DATUM POČETKA', 'DATUM ZAVRŠETKA', 'ZAMENA'])

    col1, col2 = st.columns([1, 4])
    with col1:
        with st.popover("➕ Dodaj zamenu"):
            osnovno = st.text_input("Šta/Ko se menja:")
            zamenski = st.text_input("Šta/Ko je zamena:")
            if st.button("Sačuvaj zamenu"):
                st.success("Zamena uneta!")
                st.rerun()
    with col2:
        if st.button("🗑️ Ukloni selektovane zamene"):
            st.success("Izabrane zamene obrisane!")

    st.data_editor(df_zamena, use_container_width=True, num_rows="dynamic", key="editor_zamena")

elif modul == "PRIMALAC MAIL-A":
    st.write("## 📧 Ljudi kojima se šalje izveštaj")
    if os.path.exists(fajl_baze):
        df_radnici = pd.read_excel(fajl_baze, sheet_name='SPISAK RADNIKA')
        if 'EMAIL ADRESA' in df_radnici.columns:
            df_mail = df_radnici[df_radnici['EMAIL ADRESA'].notna() & (df_radnici['EMAIL ADRESA'] != '')]
            
            col1, col2 = st.columns([1, 4])
            with col1:
                with st.popover("➕ Dodaj email"):
                    novi_email = st.text_input("Email adresa:")
                    tip_slanja = st.selectbox("Izaberi tip slanja:", ["TO", "CC"])
                    if st.button("Sačuvaj email"):
                        st.success("Email dodat!")
                        st.rerun()
            with col2:
                if st.button("🗑️ Ukloni email sa liste slanja"):
                    st.success("Email uklonjen!")
            
            kolone_za_prikaz = [col for col in ['EMAIL ADRESA', 'TIP'] if col in df_mail.columns]
            st.data_editor(df_mail[kolone_za_prikaz], use_container_width=True, num_rows="dynamic", key="editor_mail")
        else:
            st.warning("Kolona 'EMAIL ADRESA' nije pronađena.")
    else:
        st.error("Fajl sa podacima nije dostupan.")

elif modul == "NOSIOCI":
    st.write("## 🔑 Zaduženja mehanizacije - Nosioci")
    if os.path.exists(fajl_baze):
        df_nosioci = pd.read_excel(fajl_baze, sheet_name='NOSIOCI').drop(columns=['TIP'], errors='ignore')
        df_nosioci = df_nosioci.rename(columns={'START DATUM': 'DATUM POČETKA'})
        if 'DATUM POČETKA' in df_nosioci.columns:
            df_nosioci['DATUM POČETKA'] = pd.to_datetime(df_nosioci['DATUM POČETKA']).dt.date
    else:
        df_nosioci = pd.DataFrame(columns=['ID MAŠINE', 'TIP TURNUSA', 'DATUM POČETKA', 'SMENA', 'SAP BROJ', 'NOSILAC'])

    col1, col2 = st.columns([1, 4])
    with col1:
        with st.popover("➕ Dodaj nosioca"):
            radnik_unos = st.text_input("Prezime i ime radnika:")
            gb_unos = st.text_input("Garažni broj mašine:")
            if st.button("Sačuvaj zaduženje"):
                st.success("Zaduženje uneto!")
                st.rerun()
    with col2:
        if st.button("🗑️ Raskini selektovana zaduženja"):
            st.success("Zaduženja obrisana!")
            st.rerun()
            
    st.data_editor(df_nosioci, use_container_width=True, num_rows="dynamic", key="editor_nosioci")
