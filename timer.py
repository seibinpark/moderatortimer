import time
import random
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
        "duration": 15 * 60,      # 정지 상태: 남은 시간 / 실행 상태: 시작 시점 기준 초기 남은 시간
        "start_time": None,
        "running": False,
        "message": "",
        "last_update": time.time(),

        # 오리 이펙트
        "fx_until": 0.0,          # 이 시각까지 오리 표시
        "fx_seed": 0,             # 새로 발동 시 위치 랜덤을 바꾸기 위한 시드
        "fx_count": 4,            # 오리 마리 수
    }

state = get_shared_state()

query_params = st.experimental_get_query_params()
mode = query_params.get("mode", ["control"])[0]


def format_time(sec: int) -> str:
    sec = max(int(sec), 0)
    return f"{sec // 60:02d}:{sec % 60:02d}"


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


def trigger_duck_fx(seconds: float = 1.6, count: int = 4):
    state["fx_until"] = time.time() + float(seconds)
    state["fx_seed"] = int(state.get("fx_seed", 0)) + 1
    state["fx_count"] = int(count)
    state["last_update"] = time.time()


def get_stage_url() -> str:
    return "?mode=stage"


if mode == "control":
    st.experimental_set_query_params(mode="control")

    st.title("⏱ 좌장 타이머 – 컨트롤")

    stage_url = get_stage_url()
    st.markdown(f"무대 화면 링크: [{stage_url}]({stage_url})")

    # 상태 표시
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
        st.button("오리 뿅", on_click=lambda: trigger_duck_fx(1.6, 4), use_container_width=True)

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

    # control 화면도 1초마다 갱신(남은 시간 표시)
    st.autorefresh(interval=1000, key="control_refresh")


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

    # 1초 자동 갱신(깜빡임/중복 이슈 줄이기)
    st.autorefresh(interval=1000, key="stage_refresh")

    remaining = get_remaining()
    time_str = format_time(remaining)

    # 색상 로직
    color = "#FFFFFF"
    if remaining <= 60:
        color = "#FF3333" if remaining % 2 == 0 else "#FFFFFF"
    elif remaining <= 180:
        color = "#FFD700"

    # 타이머
    st.markdown(
        f"""
        <div style="height:78vh; display:flex; justify-content:center; align-items:center; background:black; position:relative;">
            <span style="font-size:18vw; font-weight:800; color:{color}; font-family:'Segoe UI', sans-serif;">
                {time_str}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 오리 이펙트: 타이머 수치 근처에 잠깐 뿅(3~4마리)
    now = time.time()
    if now < float(state.get("fx_until", 0.0)):
        seed = int(state.get("fx_seed", 0))
        random.seed(seed)

        count = int(state.get("fx_count", 4))
        # 중앙 근처 랜덤 위치(타이머 숫자 주변)
        ducks_html = []
        for i in range(count):
            dx = random.randint(-18, 18)   # vw 단위 이동
            dy = random.randint(-10, 10)   # vh 단위 이동
            delay = random.uniform(0.0, 0.25)
            size = random.uniform(5.5, 7.5)
            ducks_html.append(
                f"""
                <div class="duck" style="
                    --dx:{dx}vw; --dy:{dy}vh; --delay:{delay}s; --size:{size}vw;
                ">🦆</div>
                """
            )

        st.markdown(
            f"""
            <style>
            .duck-layer {{
              position: fixed;
              inset: 0;
              pointer-events: none;
              z-index: 9999;
            }}
            @keyframes pop {{
              0%   {{ transform: translate(var(--dx), var(--dy)) scale(0.6); opacity: 0; }}
              30%  {{ opacity: 1; }}
              70%  {{ opacity: 1; }}
              100% {{ transform: translate(var(--dx), var(--dy)) scale(1.05); opacity: 0; }}
            }}
            .duck {{
              position: fixed;
              left: 50%;
              top: 38%;
              font-size: var(--size);
              transform: translate(-50%, -50%);
              animation: pop 1.2s ease-in-out;
              animation-delay: var(--delay);
              filter: drop-shadow(0px 6px 10px rgba(0,0,0,0.35));
            }}
            </style>
            <div class="duck-layer">
              {''.join(ducks_html)}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 메시지 바: 딱 1번만 출력(중복/깜빡 문제 해결용으로 여기만 유지)
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
