import subprocess
import streamlit as st

# Run the script file
result = subprocess.Popen(["python3 verify.py s1000_g100"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
stdout, stderr = result.communicate()

# Display the terminal output
st.text("TEST")
st.text('\n'.join(stdout.decode().split('\n')[1:][:-1]))