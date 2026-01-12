import os
import streamlit as st

# This file is deprecated. 
# Please use the React Frontend (npm run dev) and FastAPI Backend (uvicorn api:app).

st.title("360D Crawler - Legacy View")
st.warning("This interface has been deprecated. Please use the new React Dashboard.")
st.write("Run the following commands to start the new app:")
st.code("uvicorn api:app --reload")
st.code("cd 360d-爬蟲系統UI && npm run dev")
