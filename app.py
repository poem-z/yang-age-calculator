import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, time

# --- 페이지 설정 ---
st.set_page_config(page_title="캐릭터 종합 관리자", page_icon="🔮", layout="wide")

# --- 세션 상태 초기화 ---
if 'char_list' not in st.session_state:
    st.session_state.char_list = []

# ==========================================
# [로직] 탄생 상징물 데이터 및 계산 함수
# ==========================================
def get_birth_symbols(month, day):
    # 1. 별자리 (Western Zodiac)
    zodiac_dates = [
        (1, 20, "염소자리", "인내, 끈기"), (2, 19, "물병자리", "창의, 자유"), (3, 20, "물고기자리", "공감, 예술"),
        (4, 20, "양자리", "용기, 열정"), (5, 21, "황소자리", "성실, 신중"), (6, 21, "쌍둥이자리", "지성, 호기심"),
        (7, 22, "게자리", "감수성, 모성"), (8, 22, "사자자리", "자신감, 리더십"), (9, 23, "처녀자리", "섬세, 완벽"),
        (10, 23, "천칭자리", "조화, 균형"), (11, 22, "전갈자리", "통찰, 비밀"), (12, 21, "사수자리", "모험, 낙천"),
        (12, 31, "염소자리", "인내, 끈기")
    ]
    # 날짜 비교를 통해 별자리 찾기
    zodiac_sign = "알 수 없음"
    zodiac_mean = ""
    for z_month, z_day, z_name, z_mean in zodiac_dates:
        if (month, day) <= (z_month, z_day):
            zodiac_sign = z_name
            zodiac_mean = z_mean
            break
            
    # 2. 탄생석 (월별 대표석 기준)
    stones = {
        1: ("가넷", "진실, 우정"), 2: ("자수정", "평화, 성실"), 3: ("아쿠아마린", "총명, 용감"),
        4: ("다이아몬드", "영원한 사랑"), 5: ("에메랄드", "행복, 행운"), 6: ("진주", "순결, 부귀"),
        7: ("루비", "열정, 위엄"), 8: ("페리도트", "부부의 행복"), 9: ("사파이어", "자애, 성실"),
        10: ("오팔", "희망, 순결"), 11: ("토파즈", "우정, 인내"), 12: ("터키석", "성공, 승리")
    }
    stone_name, stone_mean = stones.get(month, ("정보 없음", ""))

    # 3. 탄생화 (월별 대표화 기준 - 일별은 365개라 간소화)
    flowers = {
        1: ("수선화", "신비"), 2: ("제비꽃", "겸손"), 3: ("수선화", "자존심"),
        4: ("스위트피", "추억"), 5: ("은방울꽃", "희망"), 6: ("장미", "사랑"),
        7: ("라벤더", "침묵"), 8: ("해바라기", "숭배"), 9: ("다알리아", "화려"),
        10: ("카라", "순수"), 11: ("국화", "진실"), 12: ("포인세티아", "축복")
    }
    flower_name, flower_mean = flowers.get(month, ("정보 없음", ""))

    # 4. 탄생목 (생일 구간 기준)
    # 탄생목 데이터 간소화 (Celtic Tree Astrology)
    tree_ranges = [
        ((1, 1), (1, 11), "전나무", "신비"), ((1, 12), (1, 24), "느릅나무", "고결"), ((1, 25), (2, 3), "편백나무", "신의"),
        ((2, 4), (2, 8), "포플러", "비탄"), ((2, 9), (2, 18), "삼나무", "자신감"), ((2, 19), (2, 28), "소나무", "독특"),
        ((3, 1), (3, 10), "수양버들", "우수"), ((3, 11), (3, 20), "라임나무", "의심"), ((3, 21), (3, 21), "떡갈나무", "용기"),
        ((3, 22), (3, 31), "개암나무", "비범"), ((4, 1), (4, 10), "마가목", "민감"), ((4, 11), (4, 20), "단풍나무", "이해"),
        ((4, 21), (4, 30), "호두나무", "정열"), ((5, 1), (5, 14), "포플러", "비탄"), ((5, 15), (5, 24), "밤나무", "정직"),
        ((5, 25), (6, 3), "사물푸레나무", "야망"), ((6, 4), (6, 13), "자작나무", "영감"), ((6, 14), (6, 23), "무화과나무", "감수성"),
        ((6, 24), (6, 24), "자작나무", "창조"), ((6, 25), (7, 4), "사과나무", "사랑"), ((7, 5), (7, 14), "전나무", "신비"),
        ((7, 15), (7, 25), "느릅나무", "고결"), ((7, 26), (8, 4), "편백나무", "신의"), ((8, 5), (8, 13), "포플러", "비탄"),
        ((8, 14), (8, 23), "삼나무", "자신감"), ((8, 24), (9, 2), "소나무", "독특"), ((9, 3), (9, 12), "수양버들", "우수"),
        ((9, 13), (9, 22), "라임나무", "의심"), ((9, 23), (9, 23), "올리브나무", "지혜"), ((9, 24), (10, 3), "개암나무", "비범"),
        ((10, 4), (10, 13), "마가목", "민감"), ((10, 14), (10, 23), "단풍나무", "이해"), ((10, 24), (11, 11), "호두나무", "정열"),
        ((11, 12), (11, 21), "밤나무", "정직"), ((11, 22), (12, 1), "사물푸레나무", "야망"), ((12, 2), (12, 11), "자작나무", "영감"),
        ((12, 12), (12, 21), "무화과나무", "감수성"), ((12, 22), (12, 22), "너도밤나무", "창조"), ((12, 23), (12, 31), "사과나무", "사랑")
    ]
    
    tree_name, tree_mean = "정보 없음", ""
    for start, end, t_name, t_mean in tree_ranges:
        s_m, s_d = start
        e_m, e_d = end
        # 범위 체크 (같은 달 내, 혹은 달 넘어가는 경우)
        if (month == s_m and day >= s_d) or (month == e_m and day <= e_d) or (s_m != e_m and s_m < month < e_m):
            tree_name = t_name
            tree_mean = t_mean
            break

    return {
        "별자리": f"{zodiac_sign} ({zodiac_mean})",
        "탄생석": f"{stone_name} ({stone_mean})",
        "탄생화": f"{flower_name} ({flower_mean})",
        "탄생목": f"{tree_name} ({tree_mean})"
    }

# --- 공통 함수: 데이터 추가 로직 ---
def add_character(name, group, b_date, b_time=None):
    today = date.today()
    if isinstance(b_date, datetime):
        b_date = b_date.date()
    
    # 나이 계산
    man_age = today.year - b_date.year - ((today.month, today.day) < (b_date.month, b_date.day))
    korean_age = today.year - b_date.year + 1
    
    # 상징물 계산
    symbols = get_birth_symbols(b_date.month, b_date.day)
    
    # 시간 포맷팅
    if b_time:
        if isinstance(b_time, str): # 문자열로 들어온 경우 시도
             try:
                 b_time = datetime.strptime(b_time, "%H:%M").time()
                 time_str = b_time.strftime('%H:%M')
             except:
                 time_str = str(b_time)
        else:
            time_str = b_time.strftime('%H:%M')
    else:
        time_str = "미입력"

    new_data = {
        "소속": group if group else "무소속",
        "이름": name,
        "생년월일": b_date,
        "태어난 시간": time_str,
        "만 나이": man_age,
        "세는 나이": korean_age,
        **symbols # 별자리, 탄생석 등 딕셔너리 병합
    }
    st.session_state.char_list.append(new_data)

# ==========================================
# 사이드바: 입력 패널
# ==========================================
with st.sidebar:
    st.header("📝 캐릭터 등록")
    
    # 1. 개별 등록
    st.subheader("개별 추가")
    with st.form("add_one_form", clear_on_submit=True):
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            input_group = st.text_input("소속 (예: 해적단)", placeholder="무소속")
        with col_s2:
            input_name = st.text_input("이름", placeholder="루피")
            
        input_date = st.date_input("생년월일", min_value=date(1000, 1, 1), max_value=date.today())
        input_time = st.time_input("태어난 시간 (선택)", value=None)
        
        btn_add = st.form_submit_button("등록")
        if btn_add:
            if input_name:
                add_character(input_name, input_group, input_date, input_time)
                st.success(f"'{input_name}' 등록 완료!")
            else:
                st.error("이름은 필수입니다.")

    st.divider()

    # 2. 파일 일괄 등록
    st.subheader("📂 파일로 일괄 추가")
    st.markdown("""
    <small>컬럼명 예시: <b>이름, 생년월일, 소속, 시간</b><br>
    ('태어난 시간', 'Group' 등도 인식합니다)</small>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("엑셀/CSV 업로드", type=['csv', 'xlsx'])
    
    if uploaded_file and st.button("파일 병합하기"):
        try:
            if uploaded_file.name.endswith('.csv'):
                temp_df = pd.read_csv(uploaded_file)
            else:
                temp_df = pd.read_excel(uploaded_file)
            
            # 컬럼명 정리 (공백제거, 소문자화 안함-한글위주)
            temp_df.columns = [c.strip() for c in temp_df.columns]
            
            # 유사 컬럼명 매핑 찾기
            cols = temp_df.columns
            name_col = next((c for c in cols if c in ['이름', 'Name', 'character']), None)
            date_col = next((c for c in cols if c in ['생년월일', 'Birthday', 'Birth', '생일']), None)
            group_col = next((c for c in cols if c in ['소속', '그룹', 'Group', 'Team', '부대']), None)
            time_col = next((c for c in cols if c in ['시간', '태어난 시간', 'Time', 'Birth Time', '시각']), None)
            
            if name_col and date_col:
                count = 0
                for _, row in temp_df.iterrows():
                    # 이름
                    nm = row[name_col]
                    # 생일
                    dt = pd.to_datetime(row[date_col])
                    # 소속 (없으면 빈값)
                    grp = row[group_col] if group_col and not pd.isna(row[group_col]) else "무소속"
                    # 시간 (복잡한 처리)
                    tm = None
                    if time_col and not pd.isna(row[time_col]):
                        raw_time = row[time_col]
                        # 이미 datetime 객체라면 시간만 추출
                        if isinstance(raw_time, (datetime, time)):
                            tm = raw_time
                        # 문자열이라면 파싱 시도
                        elif isinstance(raw_time, str):
                            try:
                                tm = pd.to_datetime(raw_time).time()
                            except:
                                try:
                                    tm = pd.to_datetime(raw_time, format='%H:%M').time()
                                except:
                                    tm = None # 파싱 실패시 무시
                                    
                    add_character(nm, grp, dt, tm)
                    count += 1
                st.success(f"{count}명 데이터를 불러왔습니다.")
            else:
                st.error("'이름'과 '생년월일' 컬럼을 찾을 수 없습니다.")
                
        except Exception as e:
            st.error(f"파일 읽기 오류: {e}")
            
    st.divider()
    if st.button("🗑️ 리스트 전체 삭제"):
        st.session_state.char_list = []
        st.rerun()

# ==========================================
# 메인 화면
# ==========================================
st.title("🔮 캐릭터 종합 관리자")

if len(st.session_state.char_list) > 0:
    df = pd.DataFrame(st.session_state.char_list)
    
    # --- 1. 태그(소속) 필터링 ---
    all_groups = list(df['소속'].unique())
    selected_groups = st.multiselect("🔍 소속별 필터링", all_groups, default=all_groups)
    
    # 필터 적용
    filtered_df = df[df['소속'].isin(selected_groups)]
    
    # --- 2. 탭 구성 (리스트 / 타임라인) ---
    tab_list, tab_timeline, tab_export = st.tabs(["📋 리스트 보기", "📊 생년월일 타임라인", "📤 내보내기"])
    
    with tab_list:
        # 정렬 기능
        sort_col, _ = st.columns([2, 3])
        with sort_col:
            sort_opt = st.selectbox("정렬 기준", ["소속별", "생년월일(나이 많은 순)", "생년월일(나이 적은 순)", "이름순"])
        
        if sort_opt == "생년월일(나이 많은 순)":
            view_df = filtered_df.sort_values("생년월일")
        elif sort_opt == "생년월일(나이 적은 순)":
            view_df = filtered_df.sort_values("생년월일", ascending=False)
        elif sort_opt == "이름순":
            view_df = filtered_df.sort_values("이름")
        else: # 소속별
            view_df = filtered_df.sort_values(["소속", "이름"])
            
        st.dataframe(
            view_df,
            column_config={
                "생년월일": st.column_config.DateColumn("생년월일", format="YYYY-MM-DD"),
                "태어난 시간": st.column_config.TextColumn("시간"),
                "만 나이": st.column_config.NumberColumn("만 나이", format="%d세"),
            },
            use_container_width=True,
            hide_index=True
        )
        
    with tab_timeline:
        st.subheader("📅 캐릭터 탄생 연도 타임라인")
        if not filtered_df.empty:
            # Plotly 타임라인 (Scatter plot 활용)
            fig = px.scatter(
                filtered_df,
                x="생년월일",
                y="소속",
                size="만 나이", # 점 크기는 나이에 비례 (재미요소)
                color="소속",
                hover_data=["이름", "만 나이", "별자리", "탄생화"],
                text="이름",
                title="시간 흐름에 따른 캐릭터 탄생 분포"
            )
            fig.update_traces(textposition='top center')
            fig.update_layout(height=500, xaxis_title="연도/날짜", yaxis_title="소속 그룹")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")
            
    with tab_export:
        st.subheader("마크다운 변환")
        
        md_text = f"| 소속 | 이름 | 생년월일 | 시간 | 나이(만) | 별자리 | 탄생석 | 탄생화 | 탄생목 |\n"
        md_text += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        
        for _, row in view_df.iterrows():
            md_text += f"| {row['소속']} | {row['이름']} | {row['생년월일']} | {row['태어난 시간']} | {row['만 나이']} | {row['별자리']} | {row['탄생석']} | {row['탄생화']} | {row['탄생목']} |\n"
            
        st.text_area("복사하기", value=md_text, height=200)
        st.download_button("Markdown 파일 다운로드", data=md_text, file_name="characters.md")

else:
    st.info("👈 왼쪽 사이드바에서 캐릭터 정보를 추가해주세요.")
    
    # 예시 데이터 생성 버튼
    if st.button("테스트용 예시 데이터 3명 추가하기"):
        add_character("루피", "밀짚모자 일당", date(1999, 5, 5), time(12, 0))
        add_character("조로", "밀짚모자 일당", date(1997, 11, 11), time(6, 30))
        add_character("에이스", "흰수염 해적단", date(1996, 1, 1), None)
        st.rerun()
