import streamlit as st
import requests
import json
import os
import pandas as pd
from datetime import datetime
import calendar
import time

# ==========================================
# 🔑 노션 연결 열쇠
# ==========================================
NOTION_TOKEN = "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"
DATABASE_ID = "391ca0b82d5380f9a277f56c69f8ed1e"

# 기존 로컬 데이터 저장용 파일
DATA_FILE = "spark_writing_data.json"

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

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "data" not in st.session_state:
    raw_data = load_data()
    if "writings" not in raw_data: raw_data["writings"] = []
    if "notes" not in raw_data: raw_data["notes"] = []
    if "daily_stats" not in raw_data: raw_data["daily_stats"] = {}
    if "categories" not in raw_data: raw_data["categories"] = ["소설1", "소설2", "소설3", "일기", "교육 에세이"]
    st.session_state.data = raw_data
data = st.session_state.data

# --- 노션 API 함수 ---
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def save_to_notion(category, chars, content):
    if NOTION_TOKEN == "여기에_노션_API_키를_넣으세요":
        return False
    url = "https://api.notion.com/v1/pages"
    today_str = datetime.today().strftime("%Y-%m-%d")
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "이름": {"title": [{"text": {"content": f"[{category}] {today_str}의 불꽃"}}]},
            "카테고리": {"rich_text": [{"text": {"content": category}}]},
            "날짜": {"date": {"start": today_str}},
            "글자수": {"number": chars},
            "내용": {"rich_text": [{"text": {"content": content[:2000]}}]} 
        }
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.status_code == 200
    except:
        return False

def fetch_from_notion():
    if NOTION_TOKEN == "여기에_노션_API_키를_넣으세요":
        return []
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            results = response.json().get("results", [])
            drawers = []
            for r in results:
                props = r["properties"]
                try:
                    title = props["이름"]["title"][0]["text"]["content"] if props["이름"]["title"] else "제목 없음"
                    cat = props["카테고리"]["rich_text"][0]["text"]["content"] if props["카테고리"]["rich_text"] else "미분류"
                    date = props["날짜"]["date"]["start"] if props["날짜"]["date"] else "날짜 없음"
                    content = props["내용"]["rich_text"][0]["text"]["content"] if props["내용"]["rich_text"] else ""
                    chars = props["글자수"]["number"] if props["글자수"]["number"] else 0
                    drawers.append({"title": title, "category": cat, "date": date, "content": content, "chars": chars})
                except Exception:
                    continue
            return drawers
        return []
    except:
        return []

# 페이지 설정
st.set_page_config(page_title="스파크 라이팅 (Spark Writing)", page_icon="🔥", layout="wide")

# 💡 스타일 커스텀 (눈이 편안하도록 전체 글씨를 진하게 덮어씌웠습니다!)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');
    
    html, body, [class*="css"], [class*="st-"], .st-emotion-cache-16txtl3, * { 
        font-family: 'Gowun Dodum', sans-serif !important; 
        font-weight: 600 !important; /* 글씨 굵기를 진하게 강제 적용 */
    }
    
    .main-title { font-size: 2.5rem; font-weight: 900 !important; color: #FF4B4B; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 1.1rem; text-align: center; color: #666; margin-bottom: 30px; font-weight: bold !important; }
    .praise-box { background-color: #FFF0F0; border-left: 5px solid #FF4B4B; padding: 20px; border-radius: 5px; margin-top: 20px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 5px 5px 0px 0px; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #FF4B4B !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🔥 스파크 라이팅</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">타오르고, 남기고, 영원히 보관하는 나만의 창작 공간</div>', unsafe_allow_html=True)

# 사이드바 설정
st.sidebar.header("🛠️ 시스템 설정")
openai_key = st.sidebar.text_input("OpenAI API Key 입력", type="password", help="칭찬 봇 및 맞춤법 검사기를 위해 필요합니다.")

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 AI 칭찬 봇 성향 조절")
bot_mode = st.sidebar.select_slider(
    "오늘의 기분에 맞게 조절하세요", 
    options=["💛", "🧡", "❤️"], 
    value="💛",
    label_visibility="collapsed"
)
st.sidebar.markdown("💛 무조건 칭찬<br>🧡 피드백 조금<br>❤️ 피드백 많이", unsafe_allow_html=True)

# AI 칭찬 및 맞춤법 검사 함수
def get_ai_response(text, mode, category):
    if not openai_key:
        time.sleep(1)
        return f"🎨 **[AI 팬 데모]** '{category}' 글 스파크가 폭발하네요! (실제 칭찬은 API 키 필요) 🎉"
    else:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            prompt_guide = {
                "💛": "오직 장점만 극찬하고 폭풍 칭찬해줘. 비판 0%.",
                "🧡": "90% 칭찬하고, 10%는 조심스러운 꿀팁 피드백.",
                "❤️": "70% 동기부여 칭찬, 30% 발전적 조언."
            }
            system_prompt = f"너는 열혈 독자이자 전문 편집자야. [지침] {prompt_guide[mode]} 작가의 글 카테고리: [{category}]."
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": text}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ AI 호출 오류: {str(e)}"

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

# 타이머 함수
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

# 탭 구성 
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 글쓰기", "💡 잔불 메모", "🗄️ 내 글 서랍", "📊 대시보드", "⚙️ 설정"])

# --- 탭 1: 메인 글쓰기 ---
with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("✍️ 창작 몰입")
        selected_cat = st.selectbox("어떤 글을 쓰시나요?", data["categories"])
        writing_text = st.text_area("불꽃을 채워보세요...", height=350)
        char_count = len(writing_text)
        st.write(f"현재 글자 수: **{char_count}** 자")
        
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
            if st.button("🚀 글 완성! 칭찬받고 노션에 저장"):
                if char_count < 10:
                    st.warning("조금만 더 스파크를 일으켜주세요!")
                else:
                    with st.spinner("노션 금고에 저장하고 AI가 글을 읽는 중..."):
                        saved = save_to_notion(selected_cat, char_count, writing_text)
                        
                        today_str = datetime.today().strftime("%Y-%m-%d")
                        data["writings"].append({"date": today_str, "category": selected_cat})
                        
                        if today_str not in data["daily_stats"]: data["daily_stats"][today_str] = {}
                        data["daily_stats"][today_str][selected_cat] = data["daily_stats"][today_str].get(selected_cat, 0) + char_count
                        save_data(data)
                        
                        praise_res = get_ai_response(writing_text, bot_mode, selected_cat)
                        
                        if saved:
                            st.success("🎉 완벽합니다! 글이 노션에 안전하게 영구 저장되었습니다.")
                        else:
                            st.warning("⚠️ 글은 기록되었으나 노션 저장에 실패했습니다. API 키를 확인해주세요.")
                        
                        st.session_state["praise_res"] = praise_res
                        st.session_state["final_text"] = writing_text

        if "corrected_text" in st.session_state:
            with st.expander("✅ 맞춤법 교정 결과 (클릭해서 열고 닫기)", expanded=True):
                st.write("아래 글을 확인 후 원본에 반영해 보세요!")
                st.text_area("교정본", st.session_state["corrected_text"], height=200)

        if "praise_res" in st.session_state and "final_text" in st.session_state:
            st.info("👇 우측 상단의 '복사' 아이콘을 누르면 브런치에 바로 붙여넣을 수 있습니다!")
            st.code(st.session_state["final_text"], language="text")
            st.markdown(f'<div class="praise-box">{st.session_state["praise_res"]}</div>', unsafe_allow_html=True)

    with col2:
        st.subheader("⏳ 타이머")
        timer_mode = st.radio("모드", ["30분 집중 ⏰", "10분 휴식 ☕"], horizontal=True)
        duration = 1800 if "집중" in timer_mode else 600
        timer_placeholder = st.empty()
        timer_placeholder.markdown(draw_circular_timer(1.0, "30:00" if "집중" in timer_mode else "10:00", "집중" in timer_mode), unsafe_allow_html=True)
        if st.button("타이머 시작"):
            is_focus = "집중" in timer_mode
            for secs in range(duration, -1, -1):
                mins, ss = divmod(secs, 60)
                timer_placeholder.markdown(draw_circular_timer(secs/duration, f"{mins:02d}:{ss:02d}", is_focus), unsafe_allow_html=True)
                time.sleep(1)
            st.balloons()

# --- 탭 2: 잔불 메모장 ---
with tab2:
    st.subheader("💡 잔불 유지")
    note_cat = st.selectbox("메모 카테고리", data["categories"], key="note_cat_sel")
    note_text = st.text_area("짤막한 아이디어를 툭 던져두세요.", height=150)
    if st.button("🔥 잔불 지피고 노션에 저장하기"):
        if note_text:
            saved = save_to_notion(note_cat, 50, note_text)
            today_str = datetime.today().strftime("%Y-%m-%d")
            data["notes"].append({"date": today_str, "category": note_cat})
            
            if today_str not in data["daily_stats"]: data["daily_stats"][today_str] = {}
            data["daily_stats"][today_str][note_cat] = data["daily_stats"][today_str].get(note_cat, 0) + 50 
            save_data(data)
            if saved:
                st.success(f"📂 노션 저장 완료! 잔불이 이어집니다.")
            else:
                st.warning("⚠️ 노션 저장 실패 (API 확인 필요)")
            st.rerun()

# --- 탭 3: 내 글 서랍 ---
with tab3:
    st.subheader("🗄️ 노션 서랍장 열어보기")
    st.write("노션에 안전하게 보관된 과거의 글과 메모를 불러옵니다.")
    if st.button("🔄 서랍장 새로고침"):
        with st.spinner("노션에서 글을 찾아오는 중입니다..."):
            drawer_data = fetch_from_notion()
            if drawer_data:
                st.success(f"총 {len(drawer_data)}개의 글을 찾아왔습니다!")
                for idx, item in enumerate(drawer_data):
                    with st.expander(f"[{item['date']}] {item['title']} ({item['chars']}자)"):
                        st.write(f"**카테고리:** {item['category']}")
                        st.text_area("내용", item['content'], height=200, disabled=True, key=f"drawer_item_{idx}")
            else:
                st.info("아직 서랍장이 비어 있거나, 노션 연결 설정이 필요합니다.")

# --- 탭 4: 무지개 불꽃 대시보드 ---
with tab4:
    st.subheader("📊 누적 성과 대시보드")
    
    st.write("### 🗓️ 이달의 창작 달력")
    st.write("**❤️ 글 쓴 날 | 💙 아이디어 남긴 날 | 💜 둘 다 한 날**")
    
    now = datetime.today()
    cal = calendar.monthcalendar(now.year, now.month)
    
    html = f"<table style='width:100%; text-align:center; border-collapse: collapse; font-size: 1.1em; margin-bottom: 30px;'>"
    html += "<tr style='background-color: #f0f2f6;'><th>월</th><th>화</th><th>수</th><th>목</th><th>금</th><th>토</th><th>일</th></tr>"
    
    for week in cal:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += "<td style='padding: 10px; border: 1px solid #ddd; background-color: #fafafa;'></td>"
            else:
                date_str = f"{now.year}-{now.month:02d}-{day:02d}"
                wrote = any(w.get("date") == date_str for w in data["writings"])
                noted = any(n.get("date") == date_str for n in data["notes"])
                
                icon = ""
                bg_color = "#ffffff"
                
                if wrote and noted: 
                    icon = "💜"
                    bg_color = "#f8f5ff"
                elif wrote: 
                    icon = "❤️"
                    bg_color = "#fff5f5"
                elif noted: 
                    icon = "💙"
                    bg_color = "#f5f5ff"
                
                html += f"<td style='padding: 15px; border: 1px solid #ddd; background-color: {bg_color}; height: 80px; vertical-align: top;'>"
                html += f"<strong>{day}</strong><br><span style='font-size: 1.5em;'>{icon}</span>"
                html += "</td>"
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)
    
    st.write("### 📈 카테고리별 누적 통계")
    if data["daily_stats"]:
        records = []
        for date, cats in data["daily_stats"].items():
            for cat, count in cats.items():
                records.append({"날짜": date, "카테고리": cat, "글자수": count})
        df = pd.DataFrame(records)
        df_pivot = df.groupby(["날짜", "카테고리"])["글자수"].sum().unstack().fillna(0)
        st.bar_chart(df_pivot)
    else:
        st.info("아직 누적된 통계가 없습니다.")

# --- 탭 5: 카테고리 관리 ---
with tab5:
    st.subheader("⚙️ 카테고리 설정")
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
                time.sleep(1.5)
                st.rerun()
