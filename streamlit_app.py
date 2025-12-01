import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# [설정] 여기에 구글 시트 CSV 링크를 붙여넣으세요!
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-UgtsC1edLQqidYuPTGIywS9D8sDxESOW5h3ge9v2QY/export?format=csv
"

st.set_page_config(page_title="Robot Intelligence Report", layout="wide")

@st.cache_data(ttl=600)
def load_data():
    try:
        # 링크가 비어있거나 올바르지 않으면 빈 데이터프레임 반환
        if "http" not in SHEET_URL:
            return pd.DataFrame()
        
        df = pd.read_csv(SHEET_URL)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# ---------------------------------------------------------
# 사이드바
# ---------------------------------------------------------
with st.sidebar:
    st.title("🕹️ 컨트롤 패널")
    
    selected_category = "All"
    if not df.empty and 'Category' in df.columns:
        category_list = ["All"] + list(df['Category'].unique())
        selected_category = st.selectbox("관심 카테고리", category_list)
    
    st.divider()
    today = datetime.now().date()
    start_date = st.date_input("시작일", today)
    end_date = st.date_input("종료일", today)

    st.divider()
    if st.button("🔄 데이터 새로고침"):
        st.cache_data.clear()

# ---------------------------------------------------------
# 메인 대시보드
# ---------------------------------------------------------
st.title("🤖 Robot Industry Insight")
st.markdown(f"**카카오모빌리티 로봇 사업팀_luke.kw** | {start_date} ~ {end_date}")

if not df.empty:
    # 날짜 필터링
    if 'Date' in df.columns:
        mask = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
        filtered_df = df.loc[mask]
    else:
        filtered_df = df

    # 카테고리 필터링
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]

    # 중요도 분리
    if 'Priority' in filtered_df.columns:
        high_priority_df = filtered_df[filtered_df['Priority'] == 'High']
        normal_df = filtered_df[filtered_df['Priority'] != 'High']
    else:
        high_priority_df = pd.DataFrame()
        normal_df = filtered_df

    # --- Priority Section ---
    st.header("🔥 Priority Briefing")
    if not high_priority_df.empty:
        for index, row in high_priority_df.iterrows():
            with st.container():
                st.subheader(f"[{row.get('Category','-')}] {row.get('Title','-')}")
                st.info(f"Impact: {row.get('KM_Impact', '-')}")
                st.write(row.get('Summary', '-'))
                if 'Link' in row and str(row['Link']).startswith('http'):
                    st.link_button("원문 보기", row['Link'])
                st.divider()
    else:
        st.write("중요 이슈 없음")

    # --- Global Trends Section ---
    st.header("🌍 Global Trends")
    if not normal_df.empty:
        for index, row in normal_df.iterrows():
            with st.expander(f"{row.get('Title','-')}"):
                st.write(f"요약: {row.get('Summary', '-')}")
                if 'Link' in row and str(row['Link']).startswith('http'):
                    st.markdown(f"[기사 링크]({row['Link']})")
    else:
        st.write("추가 소식 없음")

else:
    st.warning("데이터를 불러오는 중입니다. (Make가 실행되었는지, CSV 링크가 맞는지 확인해주세요)")
