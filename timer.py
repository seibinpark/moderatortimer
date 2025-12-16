import time
import random
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="좌장 타이머",
    page_icon="⏱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

@st.cache_resource
def get_shared_state():
    return {
        "duration": 15 * 60,
        "start_time": None,
        "running": False,
        "message": "",
        "last_update": time.time(),
        "fx_until": 0.0,
        "fx_seed": 0,
        "fx_count": 4,
    }
