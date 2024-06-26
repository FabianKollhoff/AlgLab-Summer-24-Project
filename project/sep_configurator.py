import streamlit as st
import streamlit_authenticator as stauth
import yaml
from benchmarks import Benchmarks
from verify import solve_sep_instance
from yaml.loader import SafeLoader

# streamlit login documentation: https://github.com/mkhorasani/Streamlit-Authenticator/tree/main?tab=readme-ov-file#authenticatelogin

with open('./login.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

st.set_page_config(
    page_title="Konfiguration - Startseite"
)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login()

if authentication_status:
    authenticator.logout()
    st.write(f'Willkommen, {name}!')
    st.write("""
    # SEP-Konfigurator
    """)

    assign_project = st.button("Projektzuordnung berechnen", type="primary")
    if assign_project:
        instance, solution = solve_sep_instance(filepath="./instances/data_s1000_g100.json")
        benchmark = Benchmarks(solution=solution, instance=instance)
        fig_rating = benchmark.log_rating_sums()
        st.pyplot(fig_rating)
        #fig_programming = benchmark.log_programming_requirements()
        #st.pyplot(fig_programming)
        #fig_friend = benchmark.log_friend_graph()
        #st.pyplot(fig_friend)
        #fig_proj_util = benchmark.log_proj_util()
        #st.pyplot(fig_proj_util)
        #fig_avg_rating = benchmark.log_avg_proj_rating()
        #st.pyplot(fig_avg_rating)

elif authentication_status is False:
    st.error('Benutzername oder Passwort ist inkorrekt.')
elif authentication_status is None:
    st.warning('Bitte gebe deinen Benutzernamen und Passwort ein.')

