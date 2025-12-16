import time
import streamlit as st

st.set_page_config(
    page_title="좌장 타이머",
    page_icon="⏱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

@st.cache_resource
def get_shared_state():
    return {
        "duration": 15 * 60,   # 정지 상태에서는 남은 시간, 실행 상태에서는 시작 시점 기준 초기 남은 시간
        "start_time": None,
        "running": False,
        "message": "",
        "last_update": time.time(),
        # 이펙트(오리) 표시용
        "fx_until": 0.0,       # 이 시간(epoch)까지 stage에 오리 표시
        "fx_text": "🦆",       # 간단 이펙트 텍스트(원하면 변경)
    }

state = get_shared_state()

query_params = st.experimental_get_query_params()
mode = query_params.get("mode", ["control"])[0]


def format_time(sec: int) -> str:
    sec = max(int(sec), 0)
    return f"{sec//60:02d}:{sec%60:02d}"


def get_remaining() -> int:
    if state["running"] and state["start_time"]:
        elapsed = time.time() - state["start_time"]
        return max(int(state["duration"] - elapsed), 0)
    return int(state["duration"])


def set_timer_seconds(total_seconds: int):
    total_seconds = max(int(total_seconds), 0)
    state["duration"] = total_seconds
    state["start_time"] = None
    state["running"] = False
    state["last_update"] = time.time()


def start_timer_from_current():
    if not state["running"]:
        state["start_time"] = time.time()
        state["running"] = True
        state["last_update"] = time.time()


def pause_timer():
    if state["running"] and state["start_time"]:
        elapsed = time.time() - state["start_time"]
        state["duration"] = max(int(state["duration"] - elapsed), 0)
        state["start_time"] = None
        state["running"] = False
        state["last_update"] = time.time()


def reset_timer_stop_only():
    state["start_time"] = None
    state["running"] = False
    state["last_update"] = time.time()


def trigger_duck_fx(seconds: float = 2.0):
    state["fx_until"] = time.time() + float(seconds)
    state["last_update"] = time.time()


def get_stage_url() -> str:
    return "?mode=stage"


if mode == "control":
    st.experimental_set_query_params(mode="control")

    st.title("⏱ 좌장 타이머 – 컨트롤")

    # Stage URL(클릭 가능)
    stage_url = get_stage_url()
    st.markdown(f"무대 화면 링크: [{stage_url}]({stage_url})")

    # 현재 상태
    remaining = get_remaining()
    status_col1, status_col2 = st.columns([1, 1])
    with status_col1:
        st.metric("남은 시간", format_time(remaining))
    with status_col2:
        st.metric("상태", "실행 중" if state["running"] else "정지")

    st.divider()

    # 시간 설정: 프리셋 + 커스텀(분/초)
    st.subheader("시간 설정")

    preset = st.radio("프리셋", [3, 5, 10, 15, 20, "custom"], horizontal=True)

    if preset == "custom":
        c1, c2 = st.columns(2)
        with c1:
            m = st.number_input("분", min_value=0, max_value=180, value=15, step=1)
        with c2:
            s = st.number_input("초", min_value=0, max_value=59, value=0, step=1)
        total_seconds = int(m) * 60 + int(s)
    else:
        total_seconds = int(preset) * 60

    if st.button("시간 적용", use_container_width=True):
        set_timer_seconds(total_seconds)
        st.success(f"{format_time(total_seconds)}로 설정했습니다")

    st.divider()

    # 제어 버튼
    st.subheader("타이머 제어")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.button("시작", on_click=start_timer_from_current, use_container_width=True)
    with c2:
        st.button("일시정지", on_click=pause_timer, use_container_width=True)
    with c3:
        st.button("리셋(정지)", on_click=reset_timer_stop_only, use_container_width=True)
    with c4:
        st.button("오리 뿅", on_click=lambda: trigger_duck_fx(2.0), use_container_width=True)

    st.divider()

    # 메시지
    st.subheader("무대 메시지")
    msg = st.text_area("무대 메시지", value=state["message"], height=110)
    m1, m2 = st.columns(2)
    with m1:
        if st.button("메시지 전송", use_container_width=True):
            state["message"] = msg.strip()
            state["last_update"] = time.time()
            st.success("메시지를 전송했습니다")
    with m2:
        if st.button("메시지 삭제", use_container_width=True):
            state["message"] = ""
            state["last_update"] = time.time()
            st.success("메시지를 삭제했습니다")

    # 컨트롤 화면도 1초마다 갱신(남은 시간 표시용)
    time.sleep(1)
    st.rerun()

else:
    st.experimental_set_query_params(mode="stage")

    # stage에서 Streamlit UI 숨김
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

    # (선택) 자동 이펙트: 60초, 30초 남았을 때 오리 잠깐
    # 원치 않으면 아래 2줄을 지우세요
    if remaining in (60, 30):
        trigger_duck_fx(1.2)

    # 타이머 출력
    st.markdown(
        f"""
        <div style="height:65vh; display:flex; justify-content:center; align-items:center; background:black; position:relative;">
            <span style="font-size:18vw; font-weight:800; color:{color}; font-family: 'Segoe UI', sans-serif;">
                {time_str}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 오리 이펙트(잠깐 표시)
    now = time.time()
    if now < float(state.get("fx_until", 0.0)):
        # 외부 오리 이미지 URL (원하면 본인 png로 교체 가능)
        duck_url = "https://upload.wikimedia.org/wikipedia/commons/3/3e/Emojione_1F986.svg"
        st.markdown(
            """
            <style>
            .duck-fx {
              position: fixed;
              right: 5vw;
              bottom: 10vh;
              font-size: 8vw;
              animation: duckPop 0.9s ease-in-out infinite alternate;
              z-index: 9999;
            }
            @keyframes duckPop {
              from { transform: translateY(0px) rotate(-8deg); opacity: 0.7; }
              to   { transform: translateY(-18px) rotate(8deg); opacity: 1.0; }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        # 이미지 대신 이모지로도 충분히 “뿅” 느낌이 납니다
        st.markdown(f'<div class="duck-fx">{state.get("fx_text","🦆")}</div>', unsafe_allow_html=True)

    # 메시지 표시
    if state["message"]:
        st.markdown(
            f"""
            <div style="background:#222; color:white; padding:20px; font-size:2.5vw; text-align:center;">
                {state["message"]}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="background:#111; color:#666; padding:12px; font-size:1.2vw; text-align:center;">
                (현재 표시할 메시지가 없습니다)
            </div>
            """,
            unsafe_allow_html=True,
        )

    # stage는 항상 1초 폴링
    time.sleep(1)
    st.rerun()
