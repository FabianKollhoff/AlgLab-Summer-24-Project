import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Login must be added for every page
with open('./login.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

st.set_page_config(
    page_title="Projekte konfigurieren"
)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login()

if authentication_status:

    st.write("""
        ## Projekt hinzufügen
        """)


    with st.form("my_form"):
        name = st.text_input("Projektname")
        capacity = st.text_input("Maximale Projektkapazität")
        min_capacity = st.text_input("Mindestteilnehmerzahl")
        veto = st.text_input("Matrikelnummer der Studierenden, die ausgeschlossen werden sollen") # currently atmost one veto possible
        st.write("Notwendige Programmierkenntnisse für die erfolgreiche Teilnahme am Projekt. 1: keine Kenntnisse, 2: Anfängerniveau, 3: fortgeschritten, 4: Expertenniveau")
        python = st.radio("Python", options=["1", "2", "3", "4"], horizontal=True)
        java = st.radio("Java", options=["1", "2", "3", "4"], horizontal=True)
        c_cpp = st.radio("C/C++", options=["1", "2", "3", "4"], horizontal=True)
        sql = st.radio("SQL", options=["1", "2", "3", "4"], horizontal=True)
        php = st.radio("PHP", options=["1", "2", "3", "4"], horizontal=True)
        submit = st.form_submit_button("Projekt erstellen")

    if submit: # wip: add error message and backend stuff
        st.success(f"Das Projekt {name} wurde angelegt.", icon="✅")

elif authentication_status is False:
    st.error('Benutzername oder Passwort ist inkorrekt.')
elif authentication_status is None:
    st.warning('Bitte gebe deinen Benutzernamen und Passwort ein.')
