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
        "duration": 15 * 60,
        "start_time": None,
        "running": False,
        "message": "",
        "last_update": time.time(),
        # fx
        "fx_until": 0.0,     # 이 시각까지 fx 표시
        "fx_seed": 0,        # fx 재발동 시 애니메이션 강제 리셋용
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
    state["fx_seed"] = int(state.get("fx_seed", 0)) + 1
    state["last_update"] = time.time()


def get_stage_url() -> str:
    return "?mode=stage"


if mode == "control":
    st.experimental_set_query_params(mode="control")

    st.title("⏱ 좌장 타이머 – 컨트롤")

    stage_url = get_stage_url()
    st.markdown(f"무대 화면 링크: [{stage_url}]({stage_url})")

    remaining = get_remaining()
    c1, c2 = st.columns([1, 1])
    with c1:
        st.metric("남은 시간", format_time(remaining))
    with c2:
        st.metric("상태", "실행 중" if state["running"] else "정지")

    st.divider()

    st.subheader("시간 설정")
    preset = st.radio("프리셋", [3, 5, 10, 15, 20, "custom"], horizontal=True)

    if preset == "custom":
        cc1, cc2 = st.columns(2)
        with cc1:
            m = st.number_input("분", min_value=0, max_value=180, value=15, step=1)
        with cc2:
            s = st.number_input("초", min_value=0, max_value=59, value=0, step=1)
        total_seconds = int(m) * 60 + int(s)
    else:
        total_seconds = int(preset) * 60

    if st.button("시간 적용", use_container_width=True):
        set_timer_seconds(total_seconds)
        st.success(f"{format_time(total_seconds)}로 설정했습니다")

    st.divider()

    st.subheader("타이머 제어")
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.button("시작", on_click=start_timer_from_current, use_container_width=True)
    with b2:
        st.button("일시정지", on_click=pause_timer, use_container_width=True)
    with b3:
        st.button("리셋(정지)", on_click=reset_timer_stop_only, use_container_width=True)
    with b4:
        st.button("오리 슝", on_click=lambda: trigger_duck_fx(2.0), use_container_width=True)

    st.divider()

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

    # 타이머 화면(메시지는 아래에서 단 1번만 출력)
    st.markdown(
        f"""
        <div style="height:78vh; display:flex; justify-content:center; align-items:center; background:black;">
            <span style="font-size:18vw; font-weight:800; color:{color}; font-family: 'Segoe UI', sans-serif;">
                {time_str}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 오리 이펙트: 화면 가운데를 왼→오로 슝 (4마리)
    now = time.time()
    if now < float(state.get("fx_until", 0.0)):
        seed = int(state.get("fx_seed", 0))
        st.markdown(
            f"""
            <style>
            .duck-layer {{
              position: fixed;
              inset: 0;
              pointer-events: none;
              z-index: 9999;
            }}
            @keyframes flyAcross {{
              0%   {{ transform: translateX(-25vw) translateY(var(--dy)) scale(1); opacity: 0; }}
              10%  {{ opacity: 1; }}
              90%  {{ opacity: 1; }}
              100% {{ transform: translateX(125vw) translateY(var(--dy)) scale(1); opacity: 0; }}
            }}
            .duck {{
              position: fixed;
              top: 42vh;
              left: 0;
              font-size: 7vw;
              animation: flyAcross 2.0s linear;
              animation-delay: var(--delay);
              transform: translateX(-25vw);
              filter: drop-shadow(0px 6px 10px rgba(0,0,0,0.35));
            }}
            </style>

            <div class="duck-layer" data-seed="{seed}">
              <div class="duck" style="--delay: 0.00s; --dy: -6vh;">🦆</div>
              <div class="duck" style="--delay: 0.15s; --dy: -1vh;">🦆</div>
              <div class="duck" style="--delay: 0.30s; --dy:  4vh;">🦆</div>
              <div class="duck" style="--delay: 0.45s; --dy:  9vh;">🦆</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 메시지 바: 딱 1번만 출력
    msg = (state.get("message") or "").strip()
    if msg:
        st.markdown(
            f"""
            <div style="background:#222; color:white; padding:20px; font-size:2.5vw; text-align:center;">
                {msg}
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

    time.sleep(1)
    st.rerun()
