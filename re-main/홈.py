# =====================================================================
# 홈.py : 사이트 첫 화면
#
# 실행 방법 (터미널에서 이 폴더로 이동한 뒤)
#     pip install -r requirements.txt
#     streamlit run 홈.py
#   → 브라우저에 http://localhost:8501 이 열린다.
#
# [수업 외] streamlit 여러 페이지 구성
#   홈.py 가 첫 화면이고 (파일 이름이 왼쪽 메뉴에 그대로 보임), pages 폴더 안의 파이썬 파일이 하나씩 메뉴(왼쪽 사이드바)가 된다.
#   파일 이름 앞의 숫자(1_, 2_ …)는 메뉴 순서, 밑줄(_)은 화면에서 띄어쓰기로 보인다.
#
# 주석 표시 규칙: [수업 N장] 수업에서 배운 코드 / [수업 외] 수업에서 안 배운 코드(자세히 설명)
# =====================================================================

import streamlit as st
import pandas as pd
import os
import plotly.express as px   # [수업 12장]
from common import emergency_banner, DATA_DIR

# [수업 외] st.set_page_config : 브라우저 탭 제목과 화면 폭 설정. 반드시 페이지 맨 처음에 한 번만 쓴다.
st.set_page_config(page_title='범죄 피해 지원 길잡이', layout='wide')

st.title('범죄 피해 지원 길잡이')
st.write('겪은 일을 고르면 받을 수 있는 지원제도를 알려 드리고, 우리 동네 범죄 현황을 지도로 보여 드립니다.')

emergency_banner()

st.subheader('무엇을 도와드릴까요?')

# [수업 외] st.columns(4) : 화면을 가로 4칸으로 나눈다. with 칸: 안에 쓴 내용이 그 칸에 들어간다.
# [수업 외] st.page_link : 다른 페이지로 가는 버튼. 복지로처럼 큰 메뉴 버튼으로 첫 화면을 구성했다.
# [수업 외] st.container(border=True) : 테두리 있는 상자 → 버튼이 카드처럼 보이게 한다.
c1, c2, c3, c4 = st.columns(4)
with c1, st.container(border=True):
    st.page_link('pages/1_내_상황_찾기.py', label='**내 상황 찾기 →**')
    st.caption('겪은 일을 체크하면 받을 수 있는 지원제도를 안내합니다')
with c2, st.container(border=True):
    st.page_link('pages/2_범죄_지도.py', label='**범죄 지도 →**')
    st.caption('서울 자치구 · 전국 시도별 범죄 현황을 지도로 봅니다')
with c3, st.container(border=True):
    st.page_link('pages/3_범죄_통계.py', label='**범죄 통계 →**')
    st.caption('많이 일어나는 범죄와 장소 TOP 10')
with c4, st.container(border=True):
    st.page_link('pages/4_AI_상담.py', label='**AI 상담 →**')
    st.caption('상황을 글로 설명하면 AI가 지원제도를 안내합니다')

st.divider()

# ---------------------------------------------------------------------
# 많이 찾은 상황 (README 5번: 사용자가 어떤 메뉴에 관심이 많은지 확인)
#   '내 상황 찾기' 에서 체크한 항목이 data/interest_log.csv 에 쌓인다. (개인정보는 저장하지 않음)
# ---------------------------------------------------------------------
st.subheader('사람들이 많이 찾은 상황')

log_path = os.path.join(DATA_DIR, 'interest_log.csv')
if os.path.exists(log_path):
    log = pd.read_csv(log_path)                     # [수업 4장]
    # [수업 6장] groupby + agg 로 상황별 선택 횟수 세기
    count = log.groupby('상황', as_index=False).agg(횟수=('상황', 'count'))
    count = count.sort_values('횟수')
    # [수업 12장] px.bar  (orientation='h' : 가로 막대. 상황 이름이 길어서 가로가 읽기 쉽다)
    fig = px.bar(data_frame=count, x='횟수', y='상황', orientation='h', height=300)
    st.plotly_chart(fig, use_container_width=True)   # [수업 외] plotly 그래프를 웹페이지에 넣기
else:
    st.caption('아직 기록이 없습니다. "내 상황 찾기" 에서 항목을 체크하면 여기에 모입니다.')

st.caption('이 사이트는 참고용 안내이며 법률 자문이 아닙니다. 범죄 통계: 경찰청 범죄 발생 지역별·장소별 통계(2025년).')
