import json
import os
import re
from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from data_schema import Project
from yaml.loader import SafeLoader


def create_project():
    # determine project id (only works if no projects are deleted)
    file_paths = []
    directory = "instances/projects"
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_paths.append(f"{directory}/{filename}")
    ids = [int(re.search(r'\d+', path).group()) for path in file_paths]
    id = max(ids) + 1 if len(ids) > 0 else 0

    vetos = []
    if veto != "":
        data = {
            id: veto
        }
        veto_file = "instances/veto.json"
        if os.path.exists(veto_file):
            with open(veto_file, 'r') as file:
                    existing_data = json.load(file)
        else:
            existing_data = {}

        new_veto = {
            id: int(veto)
        }
        existing_data.update(new_veto)

        with open(veto_file, 'w') as file:
            json.dump(existing_data, file, indent=2)


    data = Project(
        id=id,
        name=name,                         #TODO: add opt_size
        capacity=int(capacity),
        min_capacity=int(min_capacity),
        programming_requirements={
            "Python": int(python),
            "Java": int(java),
            "C/C++": int(c_cpp),
            "SQL": int(sql),
            "PHP": int(php),
        },
        veto=vetos
    ).model_dump_json(indent=2)

    with open(f"instances/projects/data_{id}.json", "w") as f:
        f.write(data)
    st.success(f"Das Projekt {name} wurde angelegt.", icon="✅")

def validate_inputs(name, capacity, min_capacity):
    if not name or not capacity or not min_capacity:
        st.error("Name, maximale und minimale Kapazität sind Pflichtfelder.")
        return False
    if veto != "" and not re.match(r"^\d{7}$", veto):
        st.error("Das Veto muss eine gültige Matrikelnummer mit genau 7 Zeichen sein.")
        return False
    if int(min_capacity) > int(capacity):
        st.error("Stelle sicher, dass die Mindestkapazität nicht größer als die Maximalkapazität ist.")
        return False
    return True

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
        st.write("Anzahl der Programmierer in den folgenden Sprachen für die erfolgreiche Durchführung des Projektes.")
        python = st.radio("Python", options=["0", "1", "2", "3"], horizontal=True)
        java = st.radio("Java", options=["0", "1", "2", "3"], horizontal=True)
        c_cpp = st.radio("C/C++", options=["0", "1", "2", "3"], horizontal=True)
        sql = st.radio("SQL", options=["0", "1", "2", "3"], horizontal=True)
        php = st.radio("PHP", options=["0", "1", "2", "3"], horizontal=True)
        submit = st.form_submit_button("Projekt erstellen")

        if submit and validate_inputs(name, capacity, min_capacity):
            create_project()

elif authentication_status is False:
    st.error('Benutzername oder Passwort ist inkorrekt.')
elif authentication_status is None:
    st.warning('Bitte gebe deinen Benutzernamen und Passwort ein.')
