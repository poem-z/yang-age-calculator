import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, time
import os

# --- 페이지 설정 ---
st.set_page_config(page_title="캐릭터 종합 관리자 Pro", page_icon="🎨", layout="wide")

# --- 세션 상태 초기화 ---
if 'char_list' not in st.session_state:
    st.session_state.char_list = []

# ==========================================
# [데이터 로드] CSV 파일 읽기 (절대 경로 적용)
# ==========================================
@st.cache_data
def load_birth_data():
    # 1. 현재 파일(app.py)의 절대 경로를 찾음
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'birth_data.csv')
    
    if not os.path.exists(file_path):
        return None
    
    try:
        # 인코딩 자동 감지 시도
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp949')
            
        # 컬럼명 앞뒤 공백 제거 (안전장치)
        df.columns = [c.strip() for c in df.columns]
            
        # 날짜 매칭 키 생성
        df['key_date'] = df['월일'].astype(str).str.replace(" ", "")
        return df
    except Exception as e:
        st.error(f"CSV 로드 실패: {e}")
        return None

# 데이터 로드
birth_df = load_birth_data()

# ==========================================
# [로직] 데이터 조회 및 병합 함수
# ==========================================
def get_detailed_info(month, day):
    # 기본값 설정
    default_info = {
        "탄생화 (月)": "", "탄생화(日)": "정보 없음", "꽃말": "",
        "탄생석 (月)": "", "의미 (月)": "", "탄생석(日)": "정보 없음", "의미 (日)": "",
        "탄생목": "정보 없음", "의미": "",
        "별자리 (탄생좌)": "", "수호신": "",
        "색상 코드": "#FFFFFF", "색 이름": "정보 없음", "색 단어": "", "퍼스널리티": ""
    }
    
    if birth_df is None:
        return default_info
    
    key = f"{month}월{day}일"
    row = birth_df[birth_df['key_date'] == key]
    
    if not row.empty:
        data = row.iloc[0].to_dict()
        # 빈 값(NaN)은 빈 문자열로 처리
        for k, v in data.items():
            if pd.isna(v):
                data[k] = ""
        return data
    else:
        return default_info

# --- 공통 함수: 데이터 추가 로직 ---
def add_character(name, group, b_date, b_time=None):
    today = date.today()
    if isinstance(b_date, datetime):
        b_date = b_date.date()
    
    man_age = today.year - b_date.year - ((today.month, today.day) < (b_date.month, b_date.day))
    korean_age = today.year - b_date.year + 1
    
    # 상세 정보 가져오기
    d = get_detailed_info(b_date.month, b_date.day)
    
    # -------------------------------------------------------
    # [수정됨] 월(Month)과 일(Day) 정보 합치기 포맷팅
    # -------------------------------------------------------
    
    # 1. 탄생화: [월] 꽃 / [일] 꽃 (꽃말)
    flower_str = ""
    if d.get('탄생화 (月)'):
        flower_str += f"[월] {d['탄생화 (月)']} "
    flower_str += f"/ [일] {d.get('탄생화(日)', '')}"
    if d.get('꽃말'):
        flower_str += f" ({d['꽃말']})"
        
    # 2. 탄생석: [월] 보석(의미) / [일] 보석(의미)
    stone_str = ""
    # 월 탄생석
    if d.get('탄생석 (月)'):
        stone_str += f"[월] {d['탄생석 (月)']}"
        if d.get('의미 (月)'):
            stone_str += f"({d['의미 (月)']})"
        stone_str += " / "
    # 일 탄생석
    stone_str += f"[일] {d.get('탄생석(日)', '')}"
    if d.get('의미 (日)'):
        stone_str += f"({d['의미 (日)']})"

    # 3. 탄생목
    tree_str = f"{d.get('탄생목', '')}"
    if d.get('의미'):
        tree_str += f" ({d['의미']})"

    # 시간 처리
    time_str = "미입력"
    if b_time:
        if isinstance(b_time, str):
             try:
                 parsed = pd.to_datetime(b_time).time()
                 time_str = parsed.strftime('%H:%M')
             except:
                 try:
                     parsed = pd.to_datetime(b_time, format='%H:%M').time()
                     time_str = parsed.strftime('%H:%M')
                 except:
                     time_str = str(b_time)
        else:
            time_str = b_time.strftime('%H:%M')

    new_data = {
        "소속": group if group else "무소속",
        "이름": name,
        "생년월일": b_date,
        "태어난 시간": time_str,
        "만 나이": man_age,
        "세는 나이": korean_age,
        # 병합된 문자열 저장
        "탄생화": flower_str,
        "탄생석": stone_str,
        "탄생목": tree_str,
        "별자리": d.get('별자리 (탄생좌)', ''),
        "수호신": d.get('수호신', ''),
        "탄생색_코드": d.get('색상 코드', '#FFFFFF'),
        "탄생색_이름": d.get('색 이름', ''),
        "성격": d.get('퍼스널리티', '')
    }
    st.session_state.char_list.append(new_data)

# ==========================================
# 사이드바: 입력 패널
# ==========================================
with st.sidebar:
    st.header("📝 캐릭터 등록")
    
    if birth_df is None:
        st.warning("⚠️ 'birth_data.csv' 파일을 찾지 못했습니다. (파일 위치 확인 필요)")

    with st.expander("1. 개별 추가", expanded=True):
        with st.form("add_one_form", clear_on_submit=True):
            input_group = st.text_input("소속", placeholder="무소속")
            input_name = st.text_input("이름")
            input_date = st.date_input("생년월일", min_value=date(1000, 1, 1), max_value=date.today())
            input_time = st.time_input("태어난 시간", value=None)
            
            if st.form_submit_button("등록"):
                if input_name:
                    add_character(input_name, input_group, input_date, input_time)
                    st.success(f"등록 완료!")
                else:
                    st.error("이름을 입력하세요.")

    with st.expander("2. 파일로 일괄 추가"):
        uploaded_file = st.file_uploader("엑셀/CSV 업로드", type=['csv', 'xlsx'])
        if uploaded_file and st.button("파일 병합"):
            try:
                if uploaded_file.name.endswith('.csv'):
                    temp_df = pd.read_csv(uploaded_file)
                else:
                    temp_df = pd.read_excel(uploaded_file)
                
                temp_df.columns = [c.strip() for c in temp_df.columns]
                cols = temp_df.columns
                
                name_col = next((c for c in cols if c in ['이름', 'Name', 'character']), None)
                date_col = next((c for c in cols if c in ['생년월일', 'Birthday', 'Birth']), None)
                group_col = next((c for c in cols if c in ['소속', '그룹', 'Group']), None)
                time_col = next((c for c in cols if c in ['시간', '태어난 시간', 'Time']), None)
                
                if name_col and date_col:
                    count = 0
                    for _, row in temp_df.iterrows():
                        nm = row[name_col]
                        dt = pd.to_datetime(row[date_col])
                        grp = row[group_col] if group_col and not pd.isna(row[group_col]) else "무소속"
                        tm = row[time_col] if time_col and not pd.isna(row[time_col]) else None
                        add_character(nm, grp, dt, tm)
                        count += 1
                    st.success(f"{count}명 추가됨!")
                else:
                    st.error("필수 컬럼(이름, 생년월일) 미발견")
            except Exception as e:
                st.error(f"오류: {e}")
            
    st.divider()
    if st.button("🗑️ 리스트 초기화"):
        st.session_state.char_list = []
        st.rerun()

# ==========================================
# 메인 화면
# ==========================================
st.title("🎨 캐릭터 상세 관리자")

if len(st.session_state.char_list) > 0:
    df = pd.DataFrame(st.session_state.char_list)
    
    # 필터
    all_groups = list(df['소속'].unique())
    selected_groups = st.multiselect("소속 필터", all_groups, default=all_groups)
    view_df = df[df['소속'].isin(selected_groups)]
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 리스트", "🆔 상세 카드", "📊 타임라인", "📤 내보내기"])
    
    # 탭 1: 리스트 (텍스트 줄바꿈 허용을 위해 컬럼 설정)
    with tab1:
        st.dataframe(
            view_df,
            column_config={
                "탄생색_코드": "색상",
                "탄생색_이름": "색 이름",
                "생년월일": st.column_config.DateColumn("생년월일", format="YYYY-MM-DD"),
                # 내용이 길어질 수 있으므로 너비 조정
                "탄생화": st.column_config.TextColumn("탄생화", width="medium"),
                "탄생석": st.column_config.TextColumn("탄생석", width="medium"),
            },
            hide_index=True,
            use_container_width=True
        )

    # 탭 2: 상세 카드
    with tab2:
        char_names = view_df['이름'].tolist()
        if char_names:
            selected = st.selectbox("캐릭터 선택", char_names)
            data = view_df[view_df['이름'] == selected].iloc[0]
            
            c1, c2 = st.columns([1, 2])
            with c1:
                code = data['탄생색_코드']
                st.markdown(f"""
                <div style="background-color:{code}; width:100%; height:150px; border-radius:10px; 
                display:flex; align-items:center; justify-content:center; color:#555; border:1px solid #ccc;">
                    <b>{data['탄생색_이름']}</b><br>({code})
                </div>
                """, unsafe_allow_html=True)
                st.caption(f"성격: {data['성격']}")
                
            with c2:
                st.markdown(f"### {data['이름']} ({data['소속']})")
                st.info(f"🎂 {data['생년월일']} (만 {data['만 나이']}세) | ⏰ {data['태어난 시간']}")
                
                # 병합된 데이터 출력
                st.write(f"**🌸 탄생화:** {data['탄생화']}")
                st.write(f"**💎 탄생석:** {data['탄생석']}")
                st.write(f"**🌳 탄생목:** {data['탄생목']}")
                st.write(f"**✨ 별자리:** {data['별자리']} (수호신: {data['수호신']})")

    # 탭 3: 타임라인
    with tab3:
        if not view_df.empty:
            fig = px.scatter(
                view_df, x="생년월일", y="소속", size="만 나이", color="소속",
                hover_data=["이름", "탄생화", "탄생석"], text="이름",
                title="캐릭터 탄생 연도 분포"
            )
            fig.update_traces(textposition='top center')
            st.plotly_chart(fig, use_container_width=True)

    # 탭 4: 내보내기
    with tab4:
        md = f"| 이름 | 생일 | 탄생화 | 탄생석 | 탄생색 |\n| :--- | :--- | :--- | :--- | :--- |\n"
        for _, row in view_df.iterrows():
            color = f"<span style='color:{row['탄생색_코드']}'>■</span> {row['탄생색_이름']}"
            md += f"| {row['이름']} | {row['생년월일']} | {row['탄생화']} | {row['탄생석']} | {color} |\n"
        
        st.code(md, language='markdown')
        st.download_button("Markdown 다운로드", data=md, file_name="char_info.md")

else:
    st.info("👈 캐릭터를 추가해주세요.")
    if st.button("예시 데이터 추가"):
        add_character("루피", "해적단", date(1999, 5, 5), "12:00")
        st.rerun()
