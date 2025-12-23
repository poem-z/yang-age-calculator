import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 페이지 설정 ---
st.set_page_config(page_title="나이 계산기 & 캐릭터 관리", page_icon="🎂")

st.title("🎂 나이 계산 및 캐릭터 정리기")

# --- 공통 함수: 나이 계산 로직 ---
def calculate_ages(birth_date):
    today = date.today()
    
    # birth_date가 datetime 객체일 경우 date로 변환
    if isinstance(birth_date, datetime):
        birth_date = birth_date.date()
        
    # 만 나이 계산
    # (오늘 월/일)이 (생일 월/일)보다 이전이면 1살 뺌
    man_age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    # 세는 나이 계산 (한국식: 태어나면 1살 + 새해마다 1살)
    korean_age = today.year - birth_date.year + 1
    
    return man_age, korean_age

# --- 탭 구성 ---
tab1, tab2 = st.tabs(["👤 개별 조회", "📂 파일 업로드 (캐릭터 리스트)"])

# ==========================================
# 기능 1: 개별 정보 입력 및 조회
# ==========================================
with tab1:
    st.header("개별 생년월일 조회")
    
    with st.form("individual_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("이름", placeholder="홍길동")
        with col2:
            birth_date = st.date_input("생년월일", min_value=date(1900, 1, 1), max_value=date.today())
            
        birth_time = st.time_input("태어난 시간 (선택사항)", value=None)
        
        submitted = st.form_submit_button("계산하기")
        
        if submitted:
            if name:
                man_age, korean_age = calculate_ages(birth_date)
                
                # 결과 출력
                st.divider()
                st.subheader(f"👋 안녕하세요, {name}님!")
                
                result_col1, result_col2 = st.columns(2)
                with result_col1:
                    st.info(f"**생년월일**: {birth_date.strftime('%Y년 %m월 %d일')}")
                    if birth_time:
                        st.info(f"**태어난 시간**: {birth_time.strftime('%H시 %M분')}")
                    else:
                        st.info("**태어난 시간**: 입력되지 않음")
                        
                with result_col2:
                    st.success(f"**만 나이**: {man_age}세")
                    st.warning(f"**세는 나이**: {korean_age}세")
            else:
                st.error("이름을 입력해주세요.")

# ==========================================
# 기능 2: 파일 업로드 및 일괄 정리
# ==========================================
with tab2:
    st.header("캐릭터 정보 파일 업로드")
    st.markdown("""
    **사용법:**
    1. 엑셀(.xlsx) 또는 CSV 파일을 업로드하세요.
    2. 파일에는 **'이름'**, **'생년월일'** 컬럼이 반드시 포함되어야 합니다.
    (예: 생년월일 형식은 2000-01-01 또는 2000/01/01 등)
    """)
    
    uploaded_file = st.file_uploader("파일 선택", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            # 파일 읽기
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # 필수 컬럼 확인 (공백 제거 후 비교)
            df.columns = [c.strip() for c in df.columns]
            
            if '이름' in df.columns and '생년월일' in df.columns:
                # 생년월일 형식 변환
                df['생년월일'] = pd.to_datetime(df['생년월일']).dt.date
                
                # 나이 계산 적용
                age_results = df['생년월일'].apply(calculate_ages)
                
                # 결과 데이터프레임에 추가
                df['만 나이'] = age_results.apply(lambda x: f"{x[0]}세")
                df['세는 나이'] = age_results.apply(lambda x: f"{x[1]}세")
                
                # 깔끔하게 보여줄 컬럼 순서 지정
                display_cols = ['이름', '생년월일', '만 나이', '세는 나이']
                
                # 나머지 컬럼도 있다면 뒤에 붙이기
                other_cols = [c for c in df.columns if c not in display_cols]
                final_df = df[display_cols + other_cols]
                
                st.write(f"총 **{len(df)}**명의 캐릭터 정보를 불러왔습니다.")
                st.dataframe(final_df, use_container_width=True)
                
            else:
                st.error("파일에 '이름'과 '생년월일' 컬럼이 있는지 확인해주세요.")
                
        except Exception as e:
            st.error(f"파일을 처리하는 중 오류가 발생했습니다: {e}")