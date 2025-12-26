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
# [유틸] 배경색에 따른 글자색(흰/검) 결정 함수
# ==========================================
def get_contrast_text_color(hex_color):
    """배경색에 따라 글자색(검정/흰색) 자동 결정"""
    if not isinstance(hex_color, str) or not hex_color.startswith('#'):
        return '#000000'
    
    hex_color = hex_color.lstrip('#')
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
        return '#000000' if yiq >= 128 else '#FFFFFF'
    except:
        return '#000000'

# ==========================================
# [데이터 로드] CSV 파일 읽기 (컬럼명 정규화 포함)
# ==========================================
@st.cache_data
def load_birth_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'birth_data.csv')
    
    if not os.path.exists(file_path):
        return None
    
    try:
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp949')
        
        # [중요] 컬럼명에서 모든 공백 제거 (매칭 오류 방지)
        # 예: "탄생화 (月)" -> "탄생화(月)", "탄생석(日)" -> "탄생석(日)"
        df.columns = [c.replace(" ", "") for c in df.columns]
        
        # 날짜 매칭 키 생성
        df['key_date'] = df['월일'].astype(str).str.replace(" ", "")
        return df
    except Exception as e:
        st.error(f"CSV 로드 실패: {e}")
        return None

birth_df = load_birth_data()

# ==========================================
# [로직] 데이터 조회 함수 (개선됨)
# ==========================================
def get_detailed_info(month, day):
    # 공백이 제거된 컬럼명 기준으로 기본값 설정
    default_info = {
        "탄생화(月)": "", "탄생화(日)": "", "탄생화(영문)": "", "꽃말": "",
        "탄생석(月)": "", "의미(月)": "", "탄생석(日)": "", "의미(日)": "",
        "탄생목": "", "의미": "",
        "별자리(탄생좌)": "", "수호신": "",
        "색상코드": "#FFFFFF", "색이름": "정보 없음", "색단어": "", "퍼스널리티": ""
    }
    
    if birth_df is None:
        return default_info
    
    key = f"{month}월{day}일"
    row = birth_df[birth_df['key_date'] == key]
    
    if not row.empty:
        # 시리즈를 딕셔너리로 변환
        data = row.iloc[0].to_dict()
        
        # 빈 값(NaN) 처리
        final_data = default_info.copy()
        for k, v in data.items():
            if not pd.isna(v):
                final_data[k] = v
        return final_data
    else:
        return default_info

# --- 공통 함수: 데이터 추가 로직 ---
def add_character(name, group, b_date, b_time=None):
    today = date.today()
    if isinstance(b_date, datetime):
        b_date = b_date.date()
    
    man_age = today.year - b_date.year - ((today.month, today.day) < (b_date.month, b_date.day))
    korean_age = today.year - b_date.year + 1
    
    d = get_detailed_info(b_date.month, b_date.day)
    
    # -------------------------------------------------------
    # [데이터 포맷팅 수정] 공백 제거된 키 사용
    # -------------------------------------------------------
    
    # 1. 탄생화
    # 형식: [月] 월꽃 [日] 일꽃 영문 (꽃말)
    flower_parts = []
    if d.get('탄생화(月)'):
        flower_parts.append(f"[月] {d['탄생화(月)']}")
    
    # 일 탄생화 + 영문
    day_flower = str(d.get('탄생화(日)', '')).strip()
    day_flower_en = str(d.get('탄생화(영문)', '')).strip()
    
    day_part = ""
    if day_flower:
        day_part = f"[日] {day_flower}"
    
    if day_flower_en and day_flower_en != 'nan':
        day_part += f" {day_flower_en}"
        
    if day_part:
        flower_parts.append(day_part)
        
    flower_str = " ".join(flower_parts)
    if d.get('꽃말'):
        flower_str += f" ({d['꽃말']})"
        
    # 2. 탄생석
    # 형식: [月] 월보석 [日] 일보석 (의미)
    stone_parts = []
    if d.get('탄생석(月)'):
        stone_parts.append(f"[月] {d['탄생석(月)']}")
        
    day_stone = str(d.get('탄생석(日)', '')).strip()
    if day_stone:
        stone_parts.append(f"[日] {day_stone}")
        
    stone_str = " ".join(stone_parts)
    
    # 의미 (일별 의미 우선, 없으면 월별 의미)
    stone_mean = d.get('의미(日)') if d.get('의미(日)') else d.get('의미(月)')
    if stone_mean:
        stone_str += f" ({stone_mean})"

    # 3. 탄생목
    tree_str = f"{d.get('탄생목', '')}"
    if d.get('의미'):
        tree_str += f" ({d['의미']})"

    # 시간
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
        
        "탄생화": flower_str,
        "탄생석": stone_str,
        "탄생목": tree_str,
        "별자리": d.get('별자리(탄생좌)', ''),
        "수호신": d.get('수호신', ''),
        
        # 컬러 정보 (공백 제거된 키)
        "탄생색_코드": d.get('색상코드', '#FFFFFF'),
        "탄생색_이름": d.get('색이름', '정보 없음'),
        "성격": d.get('퍼스널리티', '')
    }
    st.session_state.char_list.append(new_data)

# ==========================================
# 사이드바: 입력 패널
# ==========================================
with st.sidebar:
    st.header("📝 캐릭터 등록")
    if birth_df is None:
        st.warning("⚠️ 'birth_data.csv' 파일이 없습니다.")

    with st.expander("1. 개별 추가", expanded=True):
        with st.form("add_one_form", clear_on_submit=True):
            input_group = st.text_input("소속", placeholder="무소속")
            input_name = st.text_input("이름")
            input_date = st.date_input("생년월일", min_value=date(1000, 1, 1), max_value=date.today())
            input_time = st.time_input("태어난 시간", value=None)
            
            if st.form_submit_button("등록"):
                if input_name:
                    add_character(input_name, input_group, input_date, input_time)
                    st.success("등록 완료!")
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
                
                # 입력 파일 컬럼 처리
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
    
    # --- 탭 1: 리스트 ---
    with tab1:
        st.dataframe(
            view_df,
            column_config={
                "탄생색_코드": "색상",
                "탄생색_이름": "색 이름",
                "생년월일": st.column_config.DateColumn("생년월일", format="YYYY-MM-DD"),
            },
            hide_index=True,
            use_container_width=True
        )

    # --- 탭 2: 상세 카드 (CSS 강화됨) ---
    with tab2:
        char_names = view_df['이름'].tolist()
        if char_names:
            selected = st.selectbox("캐릭터 선택", char_names)
            data = view_df[view_df['이름'] == selected].iloc[0]
            
            c1, c2 = st.columns([1, 2])
            
            with c1:
                bg_color = data['탄생색_코드']
                text_color = get_contrast_text_color(bg_color)
                
                # HTML: flexbox를 이용한 완벽한 중앙 정렬
                st.markdown(f"""
                <div style="
                    background-color: {bg_color};
                    width: 100%;
                    height: 160px;
                    border-radius: 12px;
                    border: 1px solid #ccc;
                    display: flex;
                    flex-direction: column;
                    align_items: center;
                    justify_content: center;
                    text-align: center;
                    color: {text_color};
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    margin-bottom: 15px;
                ">
                    <div style="font-size: 1.3em; font-weight: bold; margin-bottom: 8px; width: 100%;">
                        {data['탄생색_이름']}
                    </div>
                    <div style="font-size: 1.0em; opacity: 0.85; font-family: monospace; width: 100%;">
                        {bg_color}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 성격 텍스트 (박스 밖)
                if data['성격']:
                    st.markdown(f"""
                    <div style="
                        text-align: center;
                        font-weight: 600;
                        font-size: 1.1em;
                        color: #444;
                        padding: 12px;
                        background-color: #f8f9fa;
                        border-radius: 8px;
                        border-left: 5px solid {bg_color};
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                        line-height: 1.5;
                    ">
                        {data['성격']}
                    </div>
                    """, unsafe_allow_html=True)
                
            with c2:
                st.markdown(f"### {data['이름']} <span style='font-size:0.7em; color:gray'>| {data['소속']}</span>", unsafe_allow_html=True)
                st.markdown(f"**🎂 생년월일:** {data['생년월일']} (만 {data['만 나이']}세)")
                st.markdown(f"**⏰ 태어난 시간:** {data['태어난 시간']}")
                
                st.divider()
                
                st.markdown(f"**✨ 별자리:** {data['별자리']} (수호신: {data['수호신']})")
                st.markdown(f"**🌸 탄생화:** {data['탄생화']}")
                st.markdown(f"**💎 탄생석:** {data['탄생석']}")
                st.markdown(f"**🌳 탄생목:** {data['탄생목']}")

    # --- 탭 3: 타임라인 ---
    with tab3:
        if not view_df.empty:
            fig = px.scatter(
                view_df, x="생년월일", y="소속", size="만 나이", color="소속",
                hover_data=["이름", "탄생화", "탄생석"], text="이름",
                title="캐릭터 탄생 연도 분포"
            )
            fig.update_traces(textposition='top center')
            st.plotly_chart(fig, use_container_width=True)

    # --- 탭 4: 내보내기 ---
    with tab4:
        md = f"| 이름 | 생일 | 탄생화 | 탄생석 | 탄생색 |\n| :--- | :--- | :--- | :--- | :--- |\n"
        for _, row in view_df.iterrows():
            color_span = f"<span style='color:{row['탄생색_코드']}'>■</span> {row['탄생색_이름']}"
            md += f"| {row['이름']} | {row['생년월일']} | {row['탄생화']} | {row['탄생석']} | {color_span} |\n"
        
        st.code(md, language='markdown')
        st.download_button("Markdown 다운로드", data=md, file_name="char_info.md")

else:
    st.info("👈 캐릭터를 추가해주세요.")
    if st.button("예시 데이터 추가 (루피: 5월 5일)"):
        add_character("루피", "밀짚모자 일당", date(1999, 5, 5), "12:00")
        st.rerun()
