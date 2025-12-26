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
# [데이터 로드] CSV 파일 읽기
# ==========================================
@st.cache_data # 데이터 캐싱 (속도 향상)
def load_birth_data():
    # 1. 현재 이 파이썬 파일(app.py)이 있는 폴더의 위치를 알아냅니다.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. 그 폴더 경로와 파일명을 합쳐서 정확한 주소를 만듭니다.
    file_path = os.path.join(current_dir, 'birth_data.csv')
    
    if not os.path.exists(file_path):
        # 디버깅을 위해 어디서 찾았는지 에러 메시지로 보여줍니다.
        st.error(f"파일을 찾을 수 없습니다. 탐색 경로: {file_path}") 
        return None
    
    try:
        # CSV 읽기
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp949')
            
        df['key_date'] = df['월일'].astype(str).str.replace(" ", "")
        return df
    except Exception as e:
        st.error(f"CSV 로드 실패: {e}")
        return None

# 전역 변수에 데이터 로드
birth_df = load_birth_data()

# ==========================================
# [로직] 데이터 조회 함수
# ==========================================
def get_detailed_info(month, day):
    # CSV 파일이 없으면 기본값 반환
    default_info = {
        "탄생화(日)": "정보 없음", "꽃말": "", 
        "탄생석(日)": "정보 없음", "의미 (日)": "",
        "탄생목": "정보 없음", "의미": "",
        "별자리 (탄생좌)": "", "수호신": "", "수호성": "",
        "색상 코드": "#FFFFFF", "색 이름": "정보 없음", "색 단어": "", "퍼스널리티": ""
    }
    
    if birth_df is None:
        return default_info
    
    # 키 생성 (예: 1월 1일 -> 1월1일)
    key = f"{month}월{day}일"
    
    # 검색
    row = birth_df[birth_df['key_date'] == key]
    
    if not row.empty:
        data = row.iloc[0].to_dict()
        # NaN(빈값) 처리
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
    
    # 나이 계산
    man_age = today.year - b_date.year - ((today.month, today.day) < (b_date.month, b_date.day))
    korean_age = today.year - b_date.year + 1
    
    # CSV에서 상세 정보 가져오기
    details = get_detailed_info(b_date.month, b_date.day)
    
    # 시간 포맷팅
    time_str = "미입력"
    if b_time:
        if isinstance(b_time, str):
             try:
                 # 문자열 파싱 시도
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
        # --- CSV 상세 정보 매핑 ---
        "탄생화": f"{details.get('탄생화(日)', '')} ({details.get('꽃말', '')})",
        "탄생석": f"{details.get('탄생석(日)', '')} ({details.get('의미 (日)', '')})",
        "탄생목": f"{details.get('탄생목', '')} ({details.get('의미', '')})",
        "별자리": details.get('별자리 (탄생좌)', ''),
        "수호신": details.get('수호신', ''),
        "탄생색_코드": details.get('색상 코드', '#FFFFFF'), # 컬러 표시용
        "탄생색_이름": details.get('색 이름', ''),
        "탄생색_설명": details.get('색 단어', ''),
        "성격": details.get('퍼스널리티', '')
    }
    st.session_state.char_list.append(new_data)

# ==========================================
# 사이드바: 입력 패널
# ==========================================
with st.sidebar:
    st.header("📝 캐릭터 등록")
    
    if birth_df is None:
        st.warning("⚠️ 'birth_data.csv' 파일이 없습니다. 기본 기능만 작동합니다.")

    # 1. 개별 등록
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

    # 2. 파일 일괄 등록
    with st.expander("2. 파일로 일괄 추가"):
        uploaded_file = st.file_uploader("엑셀/CSV 업로드", type=['csv', 'xlsx'])
        if uploaded_file and st.button("파일 병합"):
            try:
                if uploaded_file.name.endswith('.csv'):
                    temp_df = pd.read_csv(uploaded_file)
                else:
                    temp_df = pd.read_excel(uploaded_file)
                
                temp_df.columns = [c.strip() for c in temp_df.columns]
                
                # 컬럼 매핑 로직
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
                    st.error("필수 컬럼(이름, 생년월일)이 없습니다.")
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
    
    # 필터링
    all_groups = list(df['소속'].unique())
    selected_groups = st.multiselect("소속 필터", all_groups, default=all_groups)
    view_df = df[df['소속'].isin(selected_groups)]
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📋 리스트", "🆔 상세 프로필 카드", "📊 타임라인", "📤 내보내기"])
    
    # --- 탭 1: 리스트 (요약) ---
    with tab1:
        st.dataframe(
            view_df,
            column_config={
                "탄생색_코드": "색상 코드",
                "탄생색_이름": "탄생색",
                "생년월일": st.column_config.DateColumn("생년월일", format="YYYY-MM-DD"),
            },
            hide_index=True,
            use_container_width=True
        )

    # --- 탭 2: 상세 프로필 카드 (비주얼 중심) ---
    with tab2:
        st.subheader("🆔 캐릭터 상세 정보")
        
        # 선택 박스로 캐릭터 선택
        char_names = view_df['이름'].tolist()
        if char_names:
            selected_char_name = st.selectbox("캐릭터를 선택하세요", char_names)
            char_data = view_df[view_df['이름'] == selected_char_name].iloc[0]
            
            # 카드 디자인 (컬럼 나누기)
            c1, c2 = st.columns([1, 2])
            
            with c1:
                # 색상 박스 표시
                color_code = char_data['탄생색_코드']
                st.markdown(f"""
                <div style="
                    background-color: {color_code};
                    width: 100%;
                    height: 150px;
                    border-radius: 10px;
                    border: 1px solid #ddd;
                    display: flex;
                    align_items: center;
                    justify_content: center;
                    color: #555;
                    font-weight: bold;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                    margin-bottom: 10px;
                ">
                    {color_code}<br>{char_data['탄생색_이름']}
                </div>
                """, unsafe_allow_html=True)
                st.caption(f"🎨 퍼스널리티: {char_data['성격']}")
            
            with c2:
                st.markdown(f"### {char_data['이름']} <span style='font-size:0.6em; color:gray'>({char_data['소속']})</span>", unsafe_allow_html=True)
                st.markdown(f"**🎂 생년월일:** {char_data['생년월일']} (만 {char_data['만 나이']}세)")
                st.markdown(f"**⏰ 시간:** {char_data['태어난 시간']}")
                st.divider()
                st.markdown(f"- **✨ 별자리:** {char_data['별자리']} (수호신: {char_data['수호신']})")
                st.markdown(f"- **💎 탄생석:** {char_data['탄생석']}")
                st.markdown(f"- **🌸 탄생화:** {char_data['탄생화']}")
                st.markdown(f"- **🌳 탄생목:** {char_data['탄생목']}")

    # --- 탭 3: 타임라인 ---
    with tab3:
        if not view_df.empty:
            fig = px.scatter(
                view_df, x="생년월일", y="소속", size="만 나이", color="소속",
                hover_data=["이름", "탄생색_이름", "별자리"], text="이름",
                title="캐릭터 탄생 연도 분포"
            )
            fig.update_traces(textposition='top center')
            st.plotly_chart(fig, use_container_width=True)

    # --- 탭 4: 내보내기 (HTML 컬러 포함) ---
    with tab4:
        st.subheader("마크다운 (컬러 아이콘 포함)")
        
        md_text = f"| 이름 | 생일 | 나이 | 별자리 | 탄생석 | 탄생화 | 탄생색 |\n"
        md_text += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        
        for _, row in view_df.iterrows():
            # HTML span 태그를 사용하여 색상 박스 만들기 (마크다운 뷰어에 따라 지원 여부 다름)
            color_box = f"<span style='color:{row['탄생색_코드']}'>■</span> {row['탄생색_이름']}"
            md_text += f"| {row['이름']} | {row['생년월일']} | {row['만 나이']} | {row['별자리']} | {row['탄생석']} | {row['탄생화']} | {color_box} |\n"
            
        st.code(md_text, language='markdown')
        st.download_button("Markdown 다운로드", data=md_text, file_name="characters_color.md")

else:
    st.info("👈 왼쪽에서 캐릭터를 추가해주세요. (birth_data.csv 파일이 있어야 상세 정보가 뜹니다)")
    if st.button("테스트 데이터 생성 (루피: 5월 5일)"):
        # 테스트용: 루피(5월 5일) -> CSV에 5월 5일 데이터가 있다면 매핑됨
        add_character("루피", "해적단", date(1999, 5, 5), "12:00")
        st.rerun()
