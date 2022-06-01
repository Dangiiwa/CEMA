import streamlit as st
from favarx_forecast import favarx_forecast
from FAVARx import favarx_explore

page = st.sidebar.selectbox("Explore Or Forecast", ("Explore", "Forecast"))

if page == "Forecast":
    favarx_forecast()
else:
    favarx_explore()
