import re

import streamlit as st
from data_schema import Project
from streamlit.components.v1 import html


def create_project():
    try:
        veto = []

        data = Project(
            id=id,
            name=name,
            capacity=capacity,
            min_capacity=min_capacity,
            programming_requirements={
                "Python": int(python),
                "Java": int(java),
                "C/C++": int(c_cpp),
                "SQL": int(sql),
                "PHP": int(php),
            },
            veto=veto
        ).model_dump_json(indent=2)
        with open(f"instances/projects/data_{id}.json", "w") as f:
            f.write(data)
    except:
        message = """alert("Bitte überprüfe deine Eingaben und korrigiere sie.");"""
        js = f"<script>{message}</script>"
        html(js)

def validate_inputs(id, name, capacity, min_capacity):
    if not id or not name or not capacity or not min_capacity:
        st.error("ID, Name, maximale und minimale Kapazität sind Pflichtfelder.")
        return False
    if veto != "" and not re.match(r"^\d{7}$", veto):
        st.error("Das Veto muss eine gültige Matrikelnummer mit genau 7 Zeichen sein.")
        return False
    return True


st.write("""
        ## Projekt hinzufügen
        """)


with st.form("my_form"):
    name = st.text_input("Projektname")
    id = st.text_input("Projekt ID")
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

    if submit and validate_inputs(id, name, capacity, min_capacity): # wip: add error message and backend stuff
        create_project()
        st.success(f"Das Projekt {name} wurde angelegt.", icon="✅")
