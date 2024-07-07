import json
import os
import re
from pathlib import Path

import streamlit as st
from data_schema import Student
from streamlit.components.v1 import html


def create_student():
    try:
        friends = []
        if matr_number_first_friend != "":
            friends.append(int(matr_number_first_friend))
        if matr_number_second_friend != "":
            friends.append(int(matr_number_second_friend))

        data = Student(
            last_name=last_name,
            first_name=first_name,
            matr_number=int(matr_number),
            projects_ratings=projects_ratings,
            programming_language_ratings={
                "Python": int(python),
                "Java": int(java),
                "C/C++": int(c_cpp),
                "SQL": int(sql),
                "PHP": int(php),
            },
            friends=friends,
        ).model_dump_json(indent=2)

        path = Path("instances/students")
        path.mkdir(parents=True, exist_ok=True)
        with open(f"instances/students/data_{matr_number}.json", "w") as f:
            f.write(data)

        # comment this section if you do not want to refresh your page to input new values
        message = """
        alert("Vielen Dank, die Daten wurden abgesendet.");
        """
        js = f"<script>{message}</script>"
        html(js)

    except:
        message = """alert("Bitte überprüfe deine Eingaben und korrigiere sie.");"""
        js = f"<script>{message}</script>"
        html(js)


def validate_inputs(first_name, last_name, matr_number):
    if not first_name or not last_name or not matr_number:
        st.error("Vorname, Nachname und Matrikelnummer sind Pflichtfelder.")
        return False
    if not re.match(r"^\d{7}$", matr_number):
        st.error("Die Matrikelnummer muss genau 7 Ziffern enthalten.")
        return False
    if matr_number_first_friend != "" and not re.match(r"^\d{7}$", matr_number_first_friend):
            st.error("Die Matrikelnummer deines Freundes muss genau 7 Ziffern enthalten.")
            return False
    if matr_number_second_friend != "" and not re.match(r"^\d{7}$", matr_number_second_friend):
            st.error("Die Matrikelnummer deines Freundes muss genau 7 Ziffern enthalten.")
            return False
    if matr_number_first_friend == matr_number_second_friend and matr_number_first_friend != "" and matr_number_second_friend != "":
        st.error("Du musst zwei unterschiedliche Freunde angeben.")
        return False
    return True

st.write(
    """
# SEP - Anmeldung
Willkommen zur Anmeldung zum SEP YYYY. Die Anmeldung ist bis zum DD.MM.YY möglich.
"""
)

with st.form("my_form"):
    first_name = st.text_input("Vorname")
    last_name = st.text_input("Nachname")
    matr_number = st.text_input("Matrikelnummer")
    programme = st.selectbox(
        "Wähle deinen Studiengang",
        ["", "Informatik", "Wirtschaftsinformatik", "Informations-Systemtechnik"],
    )
    st.write(
        "Schätze im Folgenden deine Programmierkenntnisse ein. 1: keine Kenntnisse, 2: Anfängerniveau, 3: fortgeschritten, 4: Expertenniveau"
    )
    python = st.radio("Python", options=["1", "2", "3", "4"], horizontal=True)
    java = st.radio("Java", options=["1", "2", "3", "4"], horizontal=True)
    c_cpp = st.radio("C/C++", options=["1", "2", "3", "4"], horizontal=True)
    sql = st.radio("SQL", options=["1", "2", "3", "4"], horizontal=True)
    php = st.radio("PHP", options=["1", "2", "3", "4"], horizontal=True)
    st.write(
        "Gebe bis zu zwei Studierenden, mit denen du gerne zusammenarbeiten möchtest."
    )
    matr_number_first_friend = st.text_input("Student 1 Matrikelnummer")
    matr_number_second_friend = st.text_input("Student 2 Matrikelnummer")
    st.write(
        'Bitte gebe im Folgenden dein Interesse für jedes Projekt an, wobei 1 für "wenig Interesse" steht und 5 "starkes Interesse" bedeutet. Für Details zu den Projekten kannst du die verlinkten Webseiten besuchen.'
    )
    st.link_button(
        "Projektseite", "https://www.ibr.cs.tu-bs.de/courses/ss24/sep-alg-tg/"
    )

    # list all available projects
    projects_ratings = {}
    directory = 'instances/projects'
    file_names = os.listdir(directory)
    file_names.sort()
    for filename in file_names:
        print(filename)
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            with open(filepath) as file:
                project_data = json.load(file)
                project_name = project_data["name"]
                project_capacity = project_data["capacity"]
                project_min_capacity = project_data["min_capacity"]
                project_id = project_data["id"]
        projects_rating = st.radio(
            f"Projekt {project_name} ({project_min_capacity} bis {project_capacity} Studierende)",
            options=["1", "2", "3", "4", "5"],
            horizontal=True,
        )
        projects_ratings[project_id] = int(projects_rating)

    submitted = st.form_submit_button("Absenden")
    if submitted and validate_inputs(first_name, last_name, matr_number):
        create_student()
