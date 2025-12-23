import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 페이지 설정 ---
st.set_page_config(page_title="캐릭터 관리 매니저", page_icon="📜", layout="wide")

# --- 세션 상태 초기화 (데이터 저장소) ---
# 사이트가 켜져 있는 동안 데이터를 기억하기 위한 공간입니다.
if 'char_list' not in st.session_state:
    st.session_state.char_list = []

# --- 공통 함수: 나이 계산 ---
def calculate_ages(birth_date):
    today = date.today()
    if isinstance(birth_date, datetime):
        birth_date = birth_date.date()
    
    # 만 나이
    man_age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    # 세는 나이
    korean_age = today.year - birth_date.year + 1
    
    return man_age, korean_age, birth_date

# --- 공통 함수: 데이터 추가 ---
def add_character(name, b_date, b_time=None):
    man, kor, clean_date = calculate_ages(b_date)
    time_str = b_time.strftime('%H:%M') if b_time else "미입력"
    
    new_data = {
        "이름": name,
        "생년월일": clean_date,
        "태어난 시간": time_str,
        "만 나이": man,
        "세는 나이": kor
    }
    st.session_state.char_list.append(new_data)

# --- 공통 함수: 마크다운 텍스트 생성 ---
def generate_markdown(df):
    # 데이터프레임을 마크다운 표 형식 텍스트로 변환
    md = "| 이름 | 생년월일 | 태어난 시간 | 만 나이 | 세는 나이 |\n"
    md += "| :--- | :--- | :--- | :--- | :--- |\n"
    for index, row in df.iterrows():
        md += f"| {row['이름']} | {row['생년월일']} | {row['태어난 시간']} | {row['만 나이']}세 | {row['세는 나이']}세 |\n"
    return md

# ==========================================
# 사이드바: 데이터 입력 및 관리
# ==========================================
with st.sidebar:
    st.header("📝 캐릭터 등록")
    
    # 1. 개별 등록 탭
    st.subheader("1. 한 명씩 추가")
    with st.form("add_one_form", clear_on_submit=True):
        input_name = st.text_input("이름")
        input_date = st.date_input("생년월일", min_value=date(1900, 1, 1), max_value=date.today())
        input_time = st.time_input("시간 (선택)", value=None)
        
        btn_add = st.form_submit_button("리스트에 추가")
        if btn_add:
            if input_name:
                add_character(input_name, input_date, input_time)
                st.success(f"'{input_name}' 추가 완료!")
            else:
                st.error("이름을 입력하세요.")

    st.divider()

    # 2. 파일 일괄 등록 탭
    st.subheader("2. 파일로 일괄 추가")
    uploaded_file = st.file_uploader("엑셀/CSV 업로드", type=['csv', 'xlsx'])
    if uploaded_file is not None:
        if st.button("파일 데이터 병합하기"):
            try:
                if uploaded_file.name.endswith('.csv'):
                    temp_df = pd.read_csv(uploaded_file)
                else:
                    temp_df = pd.read_excel(uploaded_file)
                
                # 컬럼 공백 제거
                temp_df.columns = [c.strip() for c in temp_df.columns]
                
                if '이름' in temp_df.columns and '생년월일' in temp_df.columns:
                    count = 0
                    for _, row in temp_df.iterrows():
                        # 날짜 변환 시도
                        b_date = pd.to_datetime(row['생년월일'])
                        add_character(row['이름'], b_date)
                        count += 1
                    st.success(f"{count}명 추가 성공!")
                else:
                    st.error("파일에 '이름', '생년월일' 컬럼이 필요합니다.")
            except Exception as e:
                st.error(f"오류 발생: {e}")
    
    st.divider()
    
    # 리셋 버튼
    if st.button("🗑️ 리스트 전체 삭제"):
        st.session_state.char_list = []
        st.rerun()

# ==========================================
# 메인 화면: 리스트 출력 및 기능
# ==========================================
st.title("📜 캐릭터 정보 리스트")

# 데이터가 있을 때만 표시
if len(st.session_state.char_list) > 0:
    
    # DataFrame 변환
    df = pd.DataFrame(st.session_state.char_list)
    
    # --- 기능: 정렬 옵션 ---
    col1, col2 = st.columns([2, 1])
    with col1:
        sort_option = st.radio(
            "정렬 기준 선택:",
            ["등록순", "나이 많은 순 (연장자)", "나이 적은 순 (연소자)", "이름순"],
            horizontal=True
        )
    
    # 정렬 로직 적용
    if sort_option == "나이 많은 순 (연장자)":
        df = df.sort_values(by="생년월일", ascending=True) # 생일이 빠를수록 나이가 많음
    elif sort_option == "나이 적은 순 (연소자)":
        df = df.sort_values(by="생년월일", ascending=False)
    elif sort_option == "이름순":
        df = df.sort_values(by="이름")
    
    # 인덱스 재설정 (깔끔하게 보이기 위함)
    df = df.reset_index(drop=True)

    # --- 메인 테이블 출력 ---
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "생년월일": st.column_config.DateColumn("생년월일", format="YYYY-MM-DD"),
            "만 나이": st.column_config.NumberColumn("만 나이", format="%d세"),
            "세는 나이": st.column_config.NumberColumn("세는 나이", format="%d세"),
        }
    )
    
    st.write(f"총 **{len(df)}**명의 캐릭터가 등록되었습니다.")
    
    st.divider()
    
    # --- 기능: 마크다운 내보내기 ---
    st.subheader("📤 내보내기")
    
    # 마크다운 텍스트 생성
    md_text = generate_markdown(df)
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        st.text_area("마크다운 미리보기 (복사해서 사용 가능)", value=md_text, height=150)
        
    with col_exp2:
        st.info("아래 버튼을 누르면 .md 파일로 다운로드됩니다.")
        st.download_button(
            label="마크다운 파일 다운로드 (.md)",
            data=md_text,
            file_name="character_list.md",
            mime="text/markdown"
        )

else:
    st.info("👈 왼쪽 사이드바에서 캐릭터를 추가하거나 파일을 업로드해주세요.")
