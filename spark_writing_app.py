import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import time

# 데이터 저장용 파일 설정
DATA_FILE = "spark_writing_data.json"

# 데이터 로드 함수
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "categories": ["소설1", "소설2", "소설3", "일기", "교육 에세이"],
        "writings": [],
        "notes": [],
        "daily_stats": {}
    }

# 데이터 저장 함수
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 세션 상태 초기화
if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# 페이지 설정
st.set_page_config(page_title="스파크 라이팅 (Spark Writing)", page_icon="🔥", layout="wide")

# 스타일 커스텀
st.markdown("""
    <style>
    .main-title { font-size: 2.5rem; font-weight: bold; color: #FF4B4B; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 1.1rem; text-align: center; color: #666; margin-bottom: 30px; }
    .praise-box { background-color: #FFF0F0; border-left: 5px solid #FF4B4B; padding: 20px; border-radius: 5px; margin-top: 20px; }
    .feedback-box { background-color: #F0F4FF; border-left: 5px solid #4B79FF; padding: 20px; border-radius: 5px; margin-top: 20px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 5px 5px 0px 0px; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #FF4B4B !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🔥 스파크 라이팅 (Spark Writing) v5</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">불꽃의 열정으로 타오르고, 잔불을 유지하며, AI 팬의 응원을 받는 창작 공간</div>', unsafe_allow_html=True)

# 사이드바 설정 (최대한 깔끔하게!)
st.sidebar.header("🛠️ 시스템 설정")
openai_key = st.sidebar.text_input("OpenAI API Key 입력", type="password", help="칭찬 봇 및 맞춤법 검사기를 위해 필요합니다.")

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 AI 칭찬 봇 성향 조절")
st.sidebar.write("🟡 무조건 칭찬 | 🟠 피드백 조금 | 🔴 피드백 많이")
bot_mode = st.sidebar.select_slider(
    " ", # 글자 생략
    options=["🟡", "🟠", "🔴"],
    value="🟡"
)

# AI 응답 생성기 
def get_ai_response(text, mode, category):
    if not openai_key:
        time.sleep(1)
        return f"🎨 **[AI 팬 칭찬 데모]** '{category}' 글 스파크가 폭발하네요! (실제 칭찬은 API 키 필요) 🎉", None
    else:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            prompt_guide = {
                "🟡": "오직 장점만 극찬하고 폭풍 칭찬해줘. 비판 0%.",
                "🟠": "90% 칭찬하고, 10%는 조심스러운 꿀팁 피드백.",
                "🔴": "70% 동기부여 칭찬, 30% 발전적 조언."
            }
            system_prompt = f"너는 열혈 독자이자 전문 편집자야. [지침] {prompt_guide[mode]} 작가의 글 카테고리: [{category}]."
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": text}]
            )
            return response.choices[0].message.content, None
        except Exception as e:
            return f"❌ AI 호출 오류: {str(e)}", None

# AI 맞춤법 검사기
def get_spell_check(text):
    if not openai_key:
        return "⚠️ API 키를 입력해야 맞춤법 검사가 가능합니다."
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        system_prompt = "제공된 한국어 텍스트의 맞춤법과 띄어쓰기를 교정해줘. 원본의 문체와 감정선은 절대 훼손하지 마. 부가적인 설명 없이 오직 '교정된 텍스트'만 출력해."
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": text}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 오류 발생: {str(e)}"

# 원형 타이머
def draw_circular_timer(percent, time_str, is_focus=True):
    color = "#FFD700" if is_focus else "#4CAF50"
    circumference = 2 * 3.141592 * 40
    offset = circumference * (1 - percent)
    
    return f"""
    <div style="display: flex; justify-content: center; align-items: center; margin-top: 10px;">
        <svg width="150" height="150" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" stroke="#f0f2f6" stroke-width="8" fill="none" />
            <circle cx="50" cy="50" r="40" stroke="{color}" stroke-width="8" fill="none"
                    stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
                    stroke-linecap="round" transform="rotate(-90 50 50)" />
            <text x="50" y="55" font-size="18" text-anchor="middle" font-weight="bold" fill="#333">{time_str}</text>
        </svg>
    </div>
    """

# 탭 구성 (카테고리 설정 탭 추가됨!)
tab1, tab2, tab3, tab4 = st.tabs(["📝 메인 글쓰기", "💡 잔불 메모장", "📊 대시보드", "⚙️ 카테고리 관리"])

# --- 탭 1: 메인 글쓰기 & 타이머 ---
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("✍️ 창작에 몰입하는 시간")
        selected_cat = st.selectbox("어떤 카테고리의 글을 쓰시나요?", data["categories"])
        writing_text = st.text_area("이곳에 불꽃을 채워보세요...", height=350, key="main_writing_area")
        char_count = len(writing_text)
        st.write(f"현재 글자 수: **{char_count}** 자")
        
        # 버튼 영역을 나눔
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("✨ AI 맞춤법 검사"):
                if char_count < 2:
                    st.warning("검사할 글을 먼저 적어주세요!")
                else:
                    with st.spinner("AI가 띄어쓰기와 맞춤법을 꼼꼼히 확인 중..."):
                        corrected_text = get_spell_check(writing_text)
                        st.session_state["corrected_text"] = corrected_text
        
        with btn_col2:
            if st.button("🚀 글 완성! 칭찬 봇에게 보내기"):
                if char_count < 10:
                    st.warning("조금만 더 스파크를 일으켜주세요!")
                else:
                    with st.spinner("AI 독자가 눈을 반짝이며 글을 읽는 중..."):
                        praise_res, _ = get_ai_response(writing_text, bot_mode, selected_cat)
                        today_str = datetime.today().strftime("%Y-%m-%d")
                        data["writings"].append({"date": today_str, "category": selected_cat, "content": writing_text, "chars": char_count})
                        if today_str not in data["daily_stats"]: data["daily_stats"][today_str] = {}
                        data["daily_stats"][today_str][selected_cat] = data["daily_stats"][today_str].get(selected_cat, 0) + char_count
                        save_data(data)
                        st.success("🎉 글 저장 및 대시보드 반영 완료!")
                        st.session_state["praise_res"] = praise_res

        # 맞춤법 검사 결과 표시
        if "corrected_text" in st.session_state:
            with st.expander("✅ 맞춤법 교정 결과 (클릭해서 열고 닫기)", expanded=True):
                st.write("아래 글을 복사해서 위의 원본을 수정하세요!")
                st.text_area("교정본", st.session_state["corrected_text"], height=200)

        # 칭찬 결과 표시
        if "praise_res" in st.session_state:
            st.markdown(f'<div class="praise-box">{st.session_state["praise_res"]}</div>', unsafe_allow_html=True)

    with col2:
        st.subheader("⏳ 포모도로 타이머")
        timer_mode = st.radio("타이머 선택", ["30분 집중 ⏰", "10분 휴식 ☕"])
        duration = 1800 if "집중" in timer_mode else 600
        
        timer_placeholder = st.empty()
        timer_placeholder.markdown(draw_circular_timer(1.0, "30:00" if "집중" in timer_mode else "10:00", "집중" in timer_mode), unsafe_allow_html=True)
        
        if st.button("타이머 시작"):
            is_focus = "집중" in timer_mode
            for secs in range(duration, -1, -1):
                mins, ss = divmod(secs, 60)
                time_str = f"{mins:02d}:{ss:02d}"
                percent = secs / duration
                timer_placeholder.markdown(draw_circular_timer(percent, time_str, is_focus), unsafe_allow_html=True)
                time.sleep(1)
            st.balloons()
            st.success("타임아웃! 리듬을 유지하세요!")

# --- 탭 2: 잔불 메모장 ---
with tab2:
    st.subheader("💡 잔불 유지 메모장")
    note_cat = st.selectbox("메모할 카테고리 선택", data["categories"], key="note_cat_sel")
    note_text = st.text_area("오늘의 짤막한 생각, 아이디어를 툭 던져두세요.", height=150)
    
    if st.button("🔥 잔불 지피기 (저장)"):
        if note_text:
            today_str = datetime.today().strftime("%Y-%m-%d")
            data["notes"].append({"date": today_str, "category": note_cat, "content": note_text})
            if today_str not in data["daily_stats"]: data["daily_stats"][today_str] = {}
            data["daily_stats"][today_str][note_cat] = data["daily_stats"][today_str].get(note_cat, 0) + 50 
            save_data(data)
            st.success(f"📂 '{note_cat}' 메모 저장 완료!")
            st.rerun()
            
    if data["notes"]:
        for n in reversed(data["notes"][-5:]):
            st.info(f"[{n['date']}] **{n['category']}** : {n['content']}")

# --- 탭 3: 무지개 불꽃 대시보드 ---
with tab3:
    st.subheader("📊 무지개 불꽃 대시보드")
    if data["daily_stats"]:
        records = []
        for date, cats in data["daily_stats"].items():
            for cat, count in cats.items():
                records.append({"날짜": date, "카테고리": cat, "글자수": count})
        df = pd.DataFrame(records)
        df_pivot = df.groupby(["날짜", "카테고리"])["글자수"].sum().unstack().fillna(0)
        st.bar_chart(df_pivot)
        
        st.write("### 📅 최근 창작 불꽃 일지")
        cat_colors = ["🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "🟤", "⚫"]
        for date in sorted(data["daily_stats"].keys(), reverse=True)[:7]:
            day_cats = data["daily_stats"][date]
            icons = []
            for idx, (c, val) in enumerate(day_cats.items()):
                color_desc = cat_colors[idx % len(cat_colors)]
                icons.append(f"{color_desc} {c}({val}자)")
            st.write(f"📅 **{date}** : {' | '.join(icons)}")

# --- 탭 4: 카테고리 관리 (새로 분리됨!) ---
with tab4:
    st.subheader("⚙️ 카테고리 추가 및 수정")
    st.write("진행 중인 프로젝트가 늘어나거나 바뀌면 여기서 관리하세요.")
    
    col_cat1, col_cat2 = st.columns(2)
    
    with col_cat1:
        st.write("#### 📂 새 카테고리 만들기")
        new_cat = st.text_input("새 카테고리 이름")
        if st.button("추가") and new_cat:
            if new_cat not in data["categories"]:
                data["categories"].append(new_cat)
                save_data(data)
                st.success(f"'{new_cat}' 추가 완료!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("이미 존재하는 카테고리입니다.")

    with col_cat2:
        st.write("#### ✏️ 카테고리 이름 변경")
        old_cat = st.selectbox("변경할 기존 카테고리 선택", data["categories"])
        new_cat_name = st.text_input("바꿀 이름 입력")
        if st.button("이름 변경하기") and new_cat_name:
            if new_cat_name in data["categories"]:
                st.error("이미 존재하는 이름입니다.")
            else:
                idx = data["categories"].index(old_cat)
                data["categories"][idx] = new_cat_name
                for w in data["writings"]:
                    if w.get("category") == old_cat: w["category"] = new_cat_name
                for n in data["notes"]:
                    if n.get("category") == old_cat: n["category"] = new_cat_name
                for date, stats in data["daily_stats"].items():
                    if old_cat in stats:
                        stats[new_cat_name] = stats.pop(old_cat)
                save_data(data)
                st.success(f"'{old_cat}' -> '{new_cat_name}' 변경 완료!")
                time.sleep(1)
                st.rerun()