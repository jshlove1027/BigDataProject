# =====================================================================
# 범죄 지도 : 서울 자치구 / 전국 시도별 범죄 현황을 색칠한 지도로 보여 주는 페이지 (README 2번)
# 주석 표시 규칙: [수업 N장] 수업에서 배운 코드 / [수업 외] 수업에서 안 배운 코드(자세히 설명)
# =====================================================================

import streamlit as st
import plotly.express as px   # [수업 12장]

# [수업 외] streamlit_folium : folium 지도를 streamlit 웹페이지 안에 넣어 주는 패키지
#   주피터에서는 지도 변수를 마지막 줄에 쓰면 보였지만(수업 11장), 웹페이지에서는 이 함수가 필요하다.
from streamlit_folium import st_folium

from common import (load_crime, seoul_table, sido_table, load_geo, make_choropleth,
                    SEOUL_GEO_URL, SIDO_GEO_URL)

st.set_page_config(page_title='범죄 지도', layout='wide')
st.title('범죄 지도')

crime, _ = load_crime()

# [수업 외] 선택 메뉴
#   st.radio     : 여러 개 중 하나를 고르는 동그란 버튼 (horizontal=True: 가로로 나열)
#   st.selectbox : 펼쳐서 고르는 목록
#   고른 값이 변수에 들어가고, 바꿀 때마다 아래 지도가 다시 그려진다.
area = st.radio('지역', ['서울 자치구', '전국 시도'], horizontal=True)
# [수업 8장] unique() : 겹치지 않는 값 목록 → 앞에 '전체' 를 붙여 선택지로 사용
types = ['전체'] + list(crime['범죄대분류'].unique())
crime_type = st.selectbox('범죄 종류', types)

if area == '서울 자치구':
    df, unit = seoul_table(crime_type)
    geo = load_geo('seoul_geo.json', SEOUL_GEO_URL)
    m = make_choropleth(geo, df, '구', unit, [37.55, 126.98], 11)
    name_col = '구'
else:
    df, unit = sido_table(crime_type)
    geo = load_geo('sido_geo.json', SIDO_GEO_URL)
    m = make_choropleth(geo, df, '지도이름', unit, [36.3, 127.8], 7)
    name_col = '시도'

if unit == '발생 건수':
    st.caption('인구 자료가 아직 없어 "발생 건수" 로 표시합니다. data/seoul_gu.csv, data/sido.csv 의 인구 칸을 채우면 인구 10만 명당 건수로 바뀝니다.')

# [수업 외] 화면을 왼쪽(지도, 넓게 3) / 오른쪽(그래프, 2) 두 칸으로 나눈다.
left, right = st.columns([3, 2])
with left:
    # returned_objects=[] : 지도를 클릭해도 페이지를 다시 실행하지 않게 함 (지도가 깜빡이지 않음)
    # key : 화면 요소의 이름표. 지역·범죄 종류가 바뀌면 이름표도 바뀌게 해서 지도를 항상 새로 그리게 한다.
    st_folium(m, height=600, use_container_width=True, returned_objects=[], key=f'map_{area}_{crime_type}')
with right:
    # [수업 6장] sort_values  /  [수업 12장] px.bar
    fig = px.bar(data_frame=df.sort_values('값', ascending=True), x='값', y=name_col,
                 color='등급', orientation='h', height=600,
                 color_discrete_map={'높음': '#d7301f', '보통': '#fc8d59', '낮음': '#fdcc8a'})
    # [수업 외] st.plotly_chart : plotly 그래프를 웹페이지에 넣기
    st.plotly_chart(fig, use_container_width=True)

st.caption('색이 진할수록 범죄가 많은 지역입니다. 지역에 마우스를 올리면 값이 보입니다. 통계는 범죄가 "발생한 장소" 기준입니다. 유동인구가 많은 곳(서울 중구·종로구 등)은 높게 나올 수 있습니다.')
