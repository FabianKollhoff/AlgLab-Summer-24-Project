import streamlit as st
import re
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
            projects_ratings={0: int(projects_ratings)},
            programming_language_ratings={
                "Python": int(python),
                "Java": int(java),
                "C/C++": int(c_cpp),
                "SQL": int(sql),
                "PHP": int(php),
            },
            friends=friends,
        ).model_dump_json(indent=2)
        with open(f"instances/data_{matr_number}.json", "w") as f:
            f.write(data)
    except:
        message = """alert("Bitte überprüfe deine Eingaben und korrigiere sie.");"""
        js = f"<script>{message}</script>"
        html(js)


def show_confirmation_message():
    message = """
   alert("Vielen Dank, die Daten wurden abgesendet.");
   """
    js = f"<script>{message}</script>"
    html(js)
    create_student()

def validate_inputs(first_name, last_name, matr_number):
    if not first_name or not last_name or not matr_number:
        st.error("Vorname, Nachname und Matrikelnummer sind Pflichtfelder.")
        return False
    if not re.match(r"^\d{7}$", matr_number):
        st.error("Die Matrikelnummer muss genau 7 Ziffern enthalten.")
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
    projects_ratings = st.radio(
        "Projekt XY (6-10 Studierende)",
        options=["1", "2", "3", "4", "5"],
        horizontal=True,
    )
    #st.form_submit_button("Absenden", on_click=show_confirmation_message)
    submitted = st.form_submit_button("Absenden")
    if submitted:
        if validate_inputs(first_name, last_name, matr_number):
            st.write("Vorname:", first_name)
            st.write("Nachname:", last_name)
            st.write("Matrikelnummer:", matr_number)
            st.write("Studiengang:", programme)
            st.write("Projektinteressen:", projects_ratings)
            show_confirmation_message()
