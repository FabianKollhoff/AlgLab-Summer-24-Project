import time
from multiprocessing import Process, Value

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
import verify
import yaml
from benchmarks import Benchmarks
from combine_data import combine_data
from data_schema import Instance, Solution
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

def solve_instance(num):
    solver, instance = verify.genererate_solver("./instances/data_s100_g10.json")

    # manually generated form data
    #combine_data()  # generate instance from inputs
    #solver, instance = verify.genererate_solver("./instances/SEP_data.json")

    solution = verify.solve_next_objective(solver=solver,instance=instance)
    num.value = 0.25
    if solution == None:
        num.value = -1
        return solution, instance
    solution = verify.solve_next_objective(solver=solver,instance=instance)
    num.value = 0.5
    if solution == None:
        num.value = -1
        return solution, instance
    solution = verify.solve_next_objective(solver=solver,instance=instance)
    num.value = 0.75
    if solution == None:
        num.value = -1
        return solution, instance
    solution = verify.solve_next_objective(solver=solver,instance=instance)
    num.value = 1

    #data = solution.model_dump_json(indent=2)
    #with open("solution/solution_of_sep.json", "w") as f:
    #    f.write(data)

    return solution, instance


if authentication_status:
    authenticator.logout()
    st.write(f'Willkommen, {name}!')
    st.write("""
    # SEP-Konfigurator
    """)

    assign_project = st.button("Projektzuordnung berechnen", type="primary")
    if assign_project:
        num = Value('d', 0)
        test_data = st.empty()
        timer = st.empty()

        start = time.time_ns()
        end = time.time_ns()
        my_bar = st.progress(0, text="Progress")

        p = Process(target=solve_instance, args=(num,))
        p.start()
        while p.is_alive():
            time.sleep(0.1)
            end = time.time_ns()
            progress_text = ""

            if num.value == 0:
                progress_text = "project rating objective"      #TODO: add optimal group size objective
            elif num.value == 0.25:
                progress_text = "programming rating objective"
            elif num.value == 0.5:
                progress_text = "friends rating objective"
            elif num.value == 0.75:
                progress_text = "optimal group size objective"
            else:
                progress_text = "finished"
            timer.metric("Elapsed time:", F"{round((end-start)/1000000000, 3)}")
            my_bar.progress(num.value, text=progress_text)
        
        if num.value == -1:
            st.write("!!! INFEASABLE SOLUTION !!!")
        else:
            with open("solution/solution_of_100_1000.json") as f:
            #with open("solution/solution_of_sep.json") as f:
                solution: Solution = Solution.model_validate_json(f.read())

            with open("./instances/data_s1000_g100.json") as f:
            #with open("./instances/SEP_data.json") as f:
                instance: Instance = Instance.model_validate_json(f.read())
            benchmark = Benchmarks(solution=solution, instance=instance)

            st.write("""average ratings project""")

            y_rating, x_rating = benchmark.log_rating_sums()
            chart_data = pd.DataFrame(x_rating, y_rating)
            st.bar_chart(chart_data)

            st.write("""percentage programming requirements""")

            x,y = benchmark.log_programming_requirements()
            chart_data = pd.DataFrame(y, x)
            st.bar_chart(chart_data)

            st.write("""project utilization""")

            x,y = benchmark.log_proj_util()
            chart_data = pd.DataFrame(y, x)
            st.bar_chart(chart_data)


elif authentication_status is False:
    st.error('Benutzername oder Passwort ist inkorrekt.')
elif authentication_status is None:
    st.warning('Bitte gebe deinen Benutzernamen und Passwort ein.')

