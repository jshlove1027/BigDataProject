# =====================================================================
# 홈.py : 사이트 첫 화면 (복지로 첫 화면 구성을 참고)
#   ① 큰 안내 상자 + 겪은 일 입력칸(복지로의 '복지서비스 검색' 자리) → AI 상담으로 바로 이동
#   ② 상황별 빠른 찾기 버튼(복지로의 '대상별·생애주기별 찾기' 자리) → 내 상황 찾기에 미리 체크된 채로 이동
#   ③ 주요 메뉴 카드  ④ 숫자 요약  ⑤ 사람들이 많이 찾은 상황
#
# 실행 방법 (터미널에서 이 폴더로 이동한 뒤)
#     pip install -r requirements.txt
#     streamlit run 홈.py
#
# [수업 외] streamlit 여러 페이지 구성
#   홈.py 가 첫 화면이고, pages 폴더 안의 파이썬 파일이 하나씩 메뉴(왼쪽 사이드바)가 된다.
#   파일 이름 앞의 숫자(1_, 2_ …)는 메뉴 순서, 밑줄(_)은 화면에서 띄어쓰기로 보인다.
#
# 주석 표시 규칙: [수업 N장] 수업에서 배운 코드 / [수업 외] 수업에서 안 배운 코드(자세히 설명)
# =====================================================================

import streamlit as st
import pandas as pd
import os
import plotly.express as px   # [수업 12장]
from common import (page_setup, section, footer, SITUATIONS, DATA_DIR,
                    load_crime, load_supports, load_laws, region_columns, crime_years)

page_setup('홈', crumb=False)

# ---------------------------------------------------------------------
# ① 큰 안내 상자 + 입력칸
# ---------------------------------------------------------------------
st.markdown('<div class="gil-hero"><h1>어떤 일을 겪으셨나요?</h1>'
            '<p>겪은 일을 적거나 고르면, 법률을 근거로 어떤 피해에 해당할 수 있는지와 받을 수 있는 지원제도를 알려 드립니다.</p></div>',
            unsafe_allow_html=True)

# [수업 외] st.form : 입력칸과 버튼을 한 묶음으로 만든다. 엔터를 쳐도 버튼을 누른 것과 같다.
with st.form('home_search', border=False):
    c1, c2 = st.columns([5, 1])
    with c1:
        text = st.text_input('겪은 일', placeholder='예) 헤어진 사람이 집 앞에서 계속 기다리고 연락해요',
                             label_visibility='collapsed')
    with c2:
        go = st.form_submit_button('AI에게 묻기', type='primary', use_container_width=True)
if go and text.strip() != '':
    # [수업 외] st.session_state : 페이지를 옮겨도 값을 기억하는 저장소. 입력한 글을 AI 상담 페이지로 넘긴다.
    st.session_state['story_from_home'] = text
    st.switch_page('pages/4_AI_상담.py')   # [수업 외] 다른 페이지로 이동

# ---------------------------------------------------------------------
# ② 상황별 빠른 찾기
# ---------------------------------------------------------------------
section('상황별로 바로 찾기')
names = list(SITUATIONS.keys())
cols = st.columns(4)
for i, name in enumerate(names):   # [수업 외] enumerate : 순서 번호(i)와 값을 같이 꺼낸다
    with cols[i % 4]:               # i % 4 : 0,1,2,3,0,1,… → 4칸에 차례로 배치
        if st.button(name, key=f'sit_{i}', use_container_width=True):
            st.session_state['preselect'] = name
            st.switch_page('pages/1_내_상황_찾기.py')

# ---------------------------------------------------------------------
# ③ 주요 메뉴 카드
#   [수업 외] st.page_link 의 icon=':material/이름:' : 구글 머티리얼 아이콘을 메뉴 앞에 붙인다.
# ---------------------------------------------------------------------
section('주요 서비스')
menus = [
    ('pages/1_내_상황_찾기.py', '내 상황 찾기', ':material/checklist:', '겪은 일을 체크하면 받을 수 있는 지원제도를 카드로 보여 드립니다'),
    ('pages/4_AI_상담.py', 'AI 상담', ':material/forum:', '상황을 글로 쓰면 관련 법률 조문과 지원제도를 함께 안내합니다'),
    ('pages/2_범죄_지도.py', '범죄 지도', ':material/map:', '연도별 서울 자치구·전국 시도 범죄율을 지도로 봅니다'),
    ('pages/3_범죄_통계.py', '범죄 통계', ':material/bar_chart:', '많이 일어나는 범죄·장소와 2018~2025년 추이'),
]
cols = st.columns(4)
for col, (path, label, icon, desc) in zip(cols, menus):   # [수업 외] zip : 두 목록을 짝지어 꺼낸다
    with col, st.container(border=True, height=128):
        st.page_link(path, label=label, icon=icon)
        st.caption(desc)

# ---------------------------------------------------------------------
# ④ 숫자 요약
# ---------------------------------------------------------------------
year = crime_years()[0]
crime, _ = load_crime(year)
total = int(crime[region_columns(crime)].sum().sum())   # [수업 외] sum().sum() : 표 전체 합계
stats = [(f'{total:,}건', f'{year}년 전국 범죄 발생'),
         (f'{len(load_supports())}개', '안내하는 지원제도'),
         (f'{len(load_laws())}개', 'AI가 근거로 쓰는 법률 조문'),
         (f'{len(crime_years())}년치', '경찰청 범죄 통계')]
cols = st.columns(4)
for col, (num, label) in zip(cols, stats):
    col.markdown(f'<div class="gil-stat"><b>{num}</b><span>{label}</span></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------
# ⑤ 많이 찾은 상황 (README 5번: 사용자가 어떤 메뉴에 관심이 많은지 확인)
#   '내 상황 찾기' 에서 체크한 항목이 data/interest_log.csv 에 쌓인다. (개인정보는 저장하지 않음)
# ---------------------------------------------------------------------
section('사람들이 많이 찾은 상황')
log_path = os.path.join(DATA_DIR, 'interest_log.csv')
if os.path.exists(log_path):
    log = pd.read_csv(log_path)                     # [수업 4장]
    # [수업 6장] groupby + agg 로 상황별 선택 횟수 세기
    count = log.groupby('상황', as_index=False).agg(횟수=('상황', 'count')).sort_values('횟수')
    # [수업 12장] px.bar  (orientation='h' : 가로 막대. 상황 이름이 길어서 가로가 읽기 쉽다)
    fig = px.bar(data_frame=count, x='횟수', y='상황', orientation='h', height=300,
                 color_discrete_sequence=['#1F5FBF'])
    st.plotly_chart(fig, use_container_width=True)   # [수업 외] plotly 그래프를 웹페이지에 넣기
else:
    st.caption('아직 기록이 없습니다. "내 상황 찾기" 에서 항목을 체크하면 여기에 모입니다.')

footer()
