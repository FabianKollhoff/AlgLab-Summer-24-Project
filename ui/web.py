import streamlit as st
from streamlit.components.v1 import html


def show_confirmation_message():
   message = """
   alert("Vielen Dank, die Daten wurden abgesendet.");
   """
   js = f"<script>{message}</script>"
   html(js)

st.write("""
# SEP - Anmeldung
Willkommen zur Anmeldung zum SEP YYYY. Die Anmeldung ist bis zum DD.MM.YY möglich.
""")

with st.form("my_form"):
   first_name = st.text_input("Vorname")
   last_name = st.text_input("Nachname")
   matr_number = st.text_input("Matrikelnummer")
   programme = st.selectbox('Wähle deinen Studiengang', ['', 'Informatik','Wirtschaftsinformatik','Informations-Systemtechnik'])
   preference = st.selectbox('Gebe deine Präferenz an', ['','Frontend','Backend', 'Keine Präferenz'])
   st.write("Bitte gebe im Folgenden dein Interesse für jedes Projekt an, wobei 1 für \"wenig Interesse\" steht und 5 \"starkes Interesse\" bedeutet. Für Details zu den Projekten kannst du die verlinkten Webseiten besuchen.")
   st.link_button("Projektseite", "https://www.ibr.cs.tu-bs.de/courses/ss24/sep-alg-tg/")
   projects_ratings = st.radio('Projekt XY (6-10 Studierende)', options=["1", "2", "3", "4", "5"], horizontal=True)
   st.form_submit_button('Absenden', on_click=show_confirmation_message)


# TODO: documentation/programming/both, skills (Java, C++, C#, Python, JavaScript, SQL)
# project can have either no skill requirements or e.g. requires basic knowledge of a certain language
# teammate pairs