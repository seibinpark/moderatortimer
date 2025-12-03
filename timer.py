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

    st.markdown(
        "이 화면은 좌장/오퍼레이터가 사용하는 화면입니다\n"
        "무대 앞 PDP에는 같은 URL을 `?mode=stage`로 열어 두면 됩니다\n"
        "예: `https://your-app-url.streamlit.app/?mode=stage`"
    )

    st.write("---")

    # 1) 시간 설정
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 기본 시간 설정")

        preset = st.radio(
            "프리셋",
            options=[5, 10, 15, 20, "custom"],
            horizontal=True,
        )

        custom_min = 15
        if preset == "custom":
            custom_min = st.number_input(
                "커스텀 시간 (분)",
                min_value=1,
                max_value=180,
                value=15,
                step=1,
            )

        if st.button("시간 적용", use_container_width=True):
            minutes = preset if preset != "custom" else custom_min
            set_timer(minutes)
            st.success(f"{minutes}분으로 타이머를 설정했습니다")

    with col2:
        st.markdown("### 현재 설정")
        remaining = get_remaining()
        st.metric("남은 시간", format_time(remaining))
        st.write("동작 상태:", "실행 중" if state["running"] else "정지")

    st.write("---")

    # 2) 타이머 제어
    st.markdown("### 타이머 제어")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button("시작", use_container_width=True):
            if not state["running"]:
                state["start_time"] = time.time()
                state["running"] = True
                st.rerun()

    with c2:
        if st.button("일시정지", use_container_width=True):
            pause_timer()
            st.rerun()

    with c3:
        if st.button("재시작", use_container_width=True):
            if not state["running"]:
                state["start_time"] = time.time()
                state["running"] = True
                st.rerun()

    with c4:
        if st.button("완전 리셋", use_container_width=True):
            reset_timer()
            st.rerun()

    st.write("---")

    # 3) 무대 메시지 보내기
    st.markdown("### 무대 메시지 전송")

    message = st.text_area(
        "무대에 띄울 메시지 (예: '5분 남았습니다, 마무리 부탁드립니다')",
        value=state["message"],
        height=80,
    )

    mcol1, mcol2 = st.columns([1, 1])

    with mcol1:
        if st.button("메시지 전송", use_container_width=True):
            state["message"] = message.strip()
            state["last_update"] = time.time()
            st.success("무대 메시지를 갱신했습니다")

    with mcol2:
        if st.button("메시지 지우기", use_container_width=True):
            state["message"] = ""
            st.success("무대 메시지를 제거했습니다")

    st.write("---")

    st.caption("Tip: 무대 PDP에서는 stage 모드로 전체화면(F11)으로 띄워두면 좋습니다")


else:
    # mode == "stage"  → 무대용 전체 화면
    st.subheader("무대용 타이머 화면")

    # 남은 시간 계산
    remaining = get_remaining()
    time_str = format_time(remaining)

    # 색상/연출 로직
    # 예: 전체 시간 기준으로
    #   - 마지막 3분: 노란색
    #   - 마지막 1분: 빨간색 깜빡이
    total = max(state["duration"], 1)
    ratio = remaining / total

    color = "#FFFFFF"  # 기본 흰색
    bg_color = "#000000"

    # 마지막 1분 이하면 빨간색 깜빡이
    if remaining <= 60:
        # 초 단위로 깜빡이 효과
        if remaining % 2 == 0:
            color = "#FF3333"
        else:
            color = "#FFFFFF"
    # 마지막 3분 이하면 노란색
    elif remaining <= 180:
        color = "#FFD700"

    # 타이머 영역 스타일
    timer_html = f"""
    <div style="
        display:flex;
        justify-content:center;
        align-items:center;
        height:60vh;
        background-color:{bg_color};
    ">
        <span style="
            font-size:18vw;
            font-weight:800;
            color:{color};
            font-family: 'Segoe UI', sans-serif;
        ">
            {time_str}
        </span>
    </div>
    """

    st.markdown(timer_html, unsafe_allow_html=True)

    # 메시지 표시 영역
    msg = state["message"]

    if msg:
        msg_html = f"""
        <div style="
            width:100%;
            padding:20px;
            background-color:#222222;
            color:#FFFFFF;
            font-size:2.5vw;
            text-align:center;
            border-top:2px solid #444444;
        ">
            {msg}
        </div>
        """
        st.markdown(msg_html, unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <div style="
                width:100%;
                padding:10px;
                background-color:#111111;
                color:#555555;
                text-align:center;
                font-size:1.2vw;
            ">
                (현재 표시할 메시지가 없습니다)
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 자동 갱신: 타이머가 실행 중이면 1초마다 재실행
    if state["running"] and remaining > 0:
        time.sleep(1)
        st.rerun()
    elif remaining <= 0:
        # 0이 되면 빨간색으로 고정
        end_html = """
        <div style="
            width:100%;
            padding:15px;
            background-color:#8B0000;
            color:#FFFFFF;
            text-align:center;
            font-size:3vw;
            font-weight:700;
        ">
            발표 시간이 종료되었습니다
        </div>
        """
        st.markdown(end_html, unsafe_allow_html=True)
        # 타이머 정지
        state["running"] = False
        state["start_time"] = None
