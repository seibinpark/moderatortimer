import time
import streamlit as st

st.set_page_config(
    page_title="좌장 타이머",
    page_icon="⏱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================
# 공유 상태 (서버 메모리)
# =========================
@st.cache_resource
def get_shared_state():
    return {
        "duration": 15 * 60,      # 남은 시간 기준
        "start_time": None,       # 시작 시각
        "running": False,
        "message": "",
        "last_update": time.time(),
    }

state = get_shared_state()

# =========================
# URL 파라미터로 모드 구분
# =========================
query_params = st.experimental_get_query_params()
mode = query_params.get("mode", ["control"])[0]

# =========================
# 공통 함수
# =========================
def set_timer(minutes: int):
    state["duration"] = minutes * 60
    state["start_time"] = None
    state["running"] = False
    state["last_update"] = time.time()

def start_timer():
    state["start_time"] = time.time()
    state["running"] = True
    state["last_update"] = time.time()

def pause_timer():
    if state["running"] and state["start_time"]:
        elapsed = time.time() - state["start_time"]
        state["duration"] = max(int(state["duration"] - elapsed), 0)
        state["running"] = False
        state["start_time"] = None
        state["last_update"] = time.time()

def reset_timer():
    state["running"] = False
    state["start_time"] = None
    state["last_update"] = time.time()

def get_remaining():
    if state["running"] and state["start_time"]:
        elapsed = time.time() - state["start_time"]
        return max(int(state["duration"] - elapsed), 0)
    return int(state["duration"])

def format_time(sec):
    return f"{sec//60:02d}:{sec%60:02d}"

# =========================
# CONTROL 화면
# =========================
if mode == "control":
    st.experimental_set_query_params(mode="control")

    st.title("⏱ 좌장 타이머 – 컨트롤")

    preset = st.radio(
        "시간 설정 (분)",
        [5, 10, 15, 20, "custom"],
        horizontal=True,
    )

    if preset == "custom":
        minutes = st.number_input("분", 1, 180, 15)
    else:
        minutes = preset

    if st.button("시간 적용", use_container_width=True):
        set_timer(int(minutes))
        st.success(f"{minutes}분 설정 완료")

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.button("시작", on_click=start_timer, use_container_width=True)
    with c2:
        st.button("일시정지", on_click=pause_timer, use_container_width=True)
    with c3:
        st.button("리셋", on_click=reset_timer, use_container_width=True)

    st.divider()

    msg = st.text_area("무대 메시지", value=state["message"], height=80)

    c4, c5 = st.columns(2)
    with c4:
        if st.button("메시지 전송", use_container_width=True):
            state["message"] = msg
            state["last_update"] = time.time()
    with c5:
        if st.button("메시지 삭제", use_container_width=True):
            state["message"] = ""
            state["last_update"] = time.time()

    st.caption("무대 화면: ?mode=stage")

# =========================
# STAGE 화면
# =========================
else:
    st.experimental_set_query_params(mode="stage")

    # Streamlit UI 제거
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    remaining = get_remaining()
    time_str = format_time(remaining)

    # 색상 로직
    color = "#FFFFFF"
    if remaining <= 60:
        color = "#FF3333" if remaining % 2 == 0 else "#FFFFFF"
    elif remaining <= 180:
        color = "#FFD700"

    st.markdown(
        f"""
        <div style="height:65vh; display:flex; justify-content:center; align-items:center; background:black;">
            <span style="font-size:18vw; font-weight:800; color:{color};">
                {time_str}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if state["message"]:
        st.markdown(
            f"""
            <div style="background:#222; color:white; padding:20px; font-size:2.5vw; text-align:center;">
                {state["message"]}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ★ 핵심: 항상 1초 폴링
    time.sleep(1)
    st.rerun()
