import time
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="좌장 타이머", page_icon="⏱", layout="wide")


# 타이머 공유 상태 (모든 세션이 같이 사용하는 객체)
@st.cache_resource
def get_shared_state():
    state = {
        "duration": 15 * 60,      # 전체 시간(초)
        "start_time": None,       # 타이머 시작 시점 (epoch time)
        "running": False,         # 동작 여부
        "message": "",            # 무대 메시지
        "last_update": time.time(),
        "last_warn_pulse": 0,     # 경고 타이밍용
    }
    return state


state = get_shared_state()

# URL 파라미터로 모드 설정 (control / stage)
query_params = st.experimental_get_query_params()
mode = query_params.get("mode", ["control"])[0]  # 기본은 control

mode = st.sidebar.radio(
    "화면 모드 선택",
    options=["control", "stage"],
    format_func=lambda x: "컨트롤 화면" if x == "control" else "무대용 화면",
    index=0 if mode == "control" else 1,
)

# 모드 바꿀 때 URL도 바꿔주기 (공유용)
st.experimental_set_query_params(mode=mode)


# 편의 함수들
def set_timer(minutes: int):
    state["duration"] = int(minutes * 60)
    state["start_time"] = None
    state["running"] = False


def start_timer():
    # 지금부터 duration 초 카운트다운
    state["start_time"] = time.time()
    state["running"] = True


def pause_timer():
    # 남은 시간을 재계산하여 duration에 반영, running 끔
    if state["running"] and state["start_time"] is not None:
        elapsed = time.time() - state["start_time"]
        remaining = max(state["duration"] - elapsed, 0)
        state["duration"] = int(remaining)
        state["running"] = False
        state["start_time"] = None


def reset_timer():
    # 단순 리셋: 시작 시점 제거, 멈춤
    state["start_time"] = None
    state["running"] = False


def get_remaining():
    if state["running"] and state["start_time"] is not None:
        elapsed = time.time() - state["start_time"]
        remaining = max(state["duration"] - elapsed, 0)
        return int(remaining)
    else:
        # 정지 상태에서는 duration을 남은 시간으로 간주
        return int(state["duration"])


def format_time(seconds: int):
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"


# 화면 공통 상단 제목
st.title("⏱ 좌장 타이머")

if mode == "control":
    st.subheader("컨트롤 패널")

