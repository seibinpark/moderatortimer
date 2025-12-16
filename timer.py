import time
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
        # timer core
        "duration": 15 * 60,
        "start_time": None,
        "running": False,
        "message": "",
        "last_update": time.time(),

        # stage display settings (timer)
        "font_vw": 18.0,
        "shake": False,
        "spin": False,
        "bg_color": "#000000",

        # stage display settings (ticker message)
        "msg_color": "#FFFFFF",
        "msg_vw": 2.6,            # 메시지 폰트 크기(vw)
        "ticker_speed_s": 16,     # 작을수록 빠름
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


def get_stage_url() -> str:
    return "?mode=stage"


def pick_timer_color(remaining: int) -> str:
    if remaining <= 60:
        return "#FF3333" if remaining % 2 == 0 else "#FFFFFF"
    if remaining <= 180:
        return "#FFD700"
    return "#FFFFFF"


BG_PRESETS = {
    "검정": "#000000",
    "빨강": "#ff0000",
    "주황": "#ff7a00",
    "노랑": "#ffd400",
    "초록": "#00b050",
    "파랑": "#0070c0",
    "남색": "#002060",
    "보라": "#7030a0",
    "흰색": "#ffffff",
}

MSG_COLOR_PRESETS = {
    "흰색": "#ffffff",
    "빨강": "#ff3b30",
    "주황": "#ff9500",
    "노랑": "#ffd60a",
    "초록": "#34c759",
    "파랑": "#0a84ff",
    "남색": "#2f2bff",
    "보라": "#bf5af2",
}


if mode == "control":
    st.experimental_set_query_params(mode="control")
    st_autorefresh(interval=1000, key="control_refresh")

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

    st.subheader("타이머 세팅")
    s1, s2, s3, s4 = st.columns([1.2, 1.2, 1.2, 1.4])
    with s1:
        state["shake"] = st.toggle("지진 효과", value=bool(state.get("shake", False)))
    with s2:
        state["spin"] = st.toggle("360도 회전", value=bool(state.get("spin", False)))
    with s3:
        state["font_vw"] = st.slider(
            "타이머 폰트 크기",
            min_value=8.0,
            max_value=28.0,
            value=float(state.get("font_vw", 18.0)),
            step=0.5,
        )
    with s4:
        label = st.selectbox("배경색", list(BG_PRESETS.keys()), index=0)
        state["bg_color"] = BG_PRESETS[label]

    st.divider()

    st.subheader("무대 메시지 세팅")
    mc1, mc2 = st.columns([1.5, 1.5])
    with mc1:
        msg_label = st.selectbox("메시지 색상", list(MSG_COLOR_PRESETS.keys()), index=0)
        state["msg_color"] = MSG_COLOR_PRESETS[msg_label]
    with mc2:
        state["ticker_speed_s"] = st.slider(
            "자막 속도(느림↔빠름)",
            min_value=8,
            max_value=30,
            value=int(state.get("ticker_speed_s", 16)),
            step=1,
        )

    st.divider()

    st.subheader("시간 설정")
    preset = st.radio("프리셋(분)", [3, 5, 10, 15, 20, "custom"], horizontal=True)

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
    b1, b2, b3 = st.columns(3)
    with b1:
        st.button("시작", on_click=start_timer_from_current, use_container_width=True)
    with b2:
        st.button("일시정지", on_click=pause_timer, use_container_width=True)
    with b3:
        st.button("리셋(정지)", on_click=reset_timer_stop_only, use_container_width=True)

    st.divider()

    st.subheader("무대 메시지")
    msg = st.text_area("무대에 흘릴 메시지", value=state["message"], height=110)

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


else:
    st.experimental_set_query_params(mode="stage")
    st_autorefresh(interval=1000, key="stage_refresh")

    remaining = get_remaining()
    time_str = format_time(remaining)

    bg = state.get("bg_color", "#000000")
    font_vw = float(state.get("font_vw", 18.0))
    shake = bool(state.get("shake", False))
    spin = bool(state.get("spin", False))
    timer_color = pick_timer_color(remaining)

    msg = (state.get("message") or "").strip()
    msg_color = state.get("msg_color", "#FFFFFF")
    msg_vw = float(state.get("msg_vw", 2.6))
    speed_s = int(state.get("ticker_speed_s", 16))

    # stage에서는 Streamlit 기본 여백/흰배경을 완전히 제거
    st.markdown(
        f"""
        <style>
        html, body {{
          height: 100%;
          background: {bg};
        }}

        /* Streamlit 전체 배경/여백 제거 */
        .stApp {{
          background: {bg};
        }}
        [data-testid="stAppViewContainer"] {{
          background: {bg};
        }}
        [data-testid="stHeader"], #MainMenu, footer {{
          display: none !important;
        }}
        .block-container {{
          padding: 0 !important;
          margin: 0 !important;
          max-width: 100% !important;
        }}

        /* 전체 stage 래퍼 */
        .stage {{
          position: fixed;
          inset: 0;
          background: {bg};
          overflow: hidden;
        }}

        /* 티커 바: 검은 화면 안에서만 */
        .ticker-bar {{
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 10vh;
          background: rgba(0,0,0,0.35);
          display: flex;
          align-items: center;
          overflow: hidden;
          border-bottom: 1px solid rgba(255,255,255,0.08);
        }}

        /* 한 문장만 흘림 (오→왼) */
        .ticker-text {{
          position: absolute;
          white-space: nowrap;
          color: {msg_color};
          font-size: {msg_vw}vw;
          font-weight: 700;
          font-family: 'Segoe UI', sans-serif;
          letter-spacing: 0.02em;
          text-shadow: 0 2px 8px rgba(0,0,0,0.35);

          /* 시작: 화면 오른쪽 밖 / 끝: 왼쪽 밖 */
          transform: translateX(100%);
          animation: slide {speed_s}s linear infinite;
        }}

        @keyframes slide {{
          0%   {{ transform: translateX(110vw); }}
          100% {{ transform: translateX(-110vw); }}
        }}

        /* 타이머 영역 */
        .timer-wrap {{
          position: absolute;
          top: 10vh;
          left: 0;
          right: 0;
          bottom: 0;
          display: flex;
          justify-content: center;
          align-items: center;
        }}

        .timer-text {{
          font-size: {font_vw}vw;
          font-weight: 900;
          color: {timer_color};
          font-family: 'Segoe UI', sans-serif;
          letter-spacing: 0.02em;
          transform-origin: center center;
          user-select: none;
        }}

        @keyframes quake {{
          0%   {{ transform: translate(0,0) rotate(0deg); }}
          10%  {{ transform: translate(-2px, 2px) rotate(-1deg); }}
          20%  {{ transform: translate(-4px, 0px) rotate(1deg); }}
          30%  {{ transform: translate(4px, 2px) rotate(0deg); }}
          40%  {{ transform: translate(2px, -2px) rotate(1deg); }}
          50%  {{ transform: translate(-2px, 2px) rotate(-1deg); }}
          60%  {{ transform: translate(-4px, -2px) rotate(0deg); }}
          70%  {{ transform: translate(4px, -2px) rotate(-1deg); }}
          80%  {{ transform: translate(-2px, -2px) rotate(1deg); }}
          90%  {{ transform: translate(2px, 2px) rotate(0deg); }}
          100% {{ transform: translate(0,0) rotate(0deg); }}
        }}
        .shake {{
          animation: quake 0.45s infinite;
        }}

        @keyframes spin360 {{
          from {{ transform: rotate(0deg); }}
          to   {{ transform: rotate(360deg); }}
        }}
        .spin {{
          animation: spin360 1.4s linear infinite;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 타이머 class
    cls = ("shake" if shake else "") + (" spin" if spin else "")

    # 렌더
    ticker_html = ""
    if msg:
        ticker_html = f"""
        <div class="ticker-bar">
          <div class="ticker-text">{msg}</div>
        </div>
        """

    st.markdown(
        f"""
        <div class="stage">
          {ticker_html}
          <div class="timer-wrap">
            <div class="timer-text {cls}">{time_str}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
