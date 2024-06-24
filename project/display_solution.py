from streamlit.web import cli as stcli
import streamlit as st

import matplotlib.pyplot as plt
import numpy as np

from _alglab_utils import CHECK, main, mandatory_testcase
from benchmarks import Benchmarks
from data_schema import Solution
from solver import SepSolver

# Set the app title 
st.title('Display Solution') 
# Add a welcome message 
st.write('Displayed test solution') 

with open("solution/solution_of_10_100.json") as f:
    solution: Solution = Solution.model_validate_json(f.read())

arr = np.random.normal(1, 1, size=100)
fig, ax = plt.subplots()
ax.hist(arr, bins=20)
st.pyplot(fig)