# =====================================================================
# 범죄 통계 : 많이 일어나는 범죄 종류와 장소 TOP 10
# 주석 표시 규칙: [수업 N장] 수업에서 배운 코드 / [수업 외] 수업에서 안 배운 코드(자세히 설명)
# =====================================================================

import streamlit as st
import plotly.express as px   # [수업 12장]
from common import load_crime, filter_type, region_columns

st.set_page_config(page_title='범죄 통계', layout='wide')
st.title('범죄 통계 (전국)')

crime, place = load_crime()
crime_type = st.selectbox('범죄 종류', ['전체'] + list(crime['범죄대분류'].unique()))

data = filter_type(crime, crime_type)
place_data = filter_type(place, crime_type)

left, right = st.columns(2)

with left:
    st.subheader('많이 일어난 범죄 TOP 10')
    type_sum = data.copy()
    # [수업 외] sum(axis=1) : 가로 방향 합계. 한 범죄의 모든 지역 건수를 더해 '전국' 컬럼을 만든다.
    #   (수업에서 쓴 sum() 은 세로 방향 합계 = axis=0)
    type_sum['전국'] = type_sum[region_columns(data)].sum(axis=1)
    type_sum = type_sum.sort_values('전국', ascending=False).head(10)   # [수업 6장]
    fig = px.bar(data_frame=type_sum, x='범죄중분류', y='전국', color='범죄대분류')   # [수업 12장]
    # [수업 외] 색(범죄대분류)으로 나누면 plotly 가 같은 색끼리 모아 그려 순서가 섞인다.
    #   categoryorder='total descending' : x축을 값이 큰 순서대로 다시 정렬
    fig.update_xaxes(categoryorder='total descending')
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader('범죄가 많이 일어난 장소 TOP 10')
    place_sum = place_data[place_data.columns[2:]].sum().reset_index()   # [수업 외] reset_index: common.py 설명 참고
    place_sum.columns = ['장소', '건수']
    # [수업 외] '_' 를 ' · ' 로 바꿔 읽기 쉽게 (예: 통행로_보도_골목길 → 통행로 · 보도 · 골목길)
    place_sum['장소'] = place_sum['장소'].str.replace('_', ' · ')
    place_sum = place_sum.sort_values('건수', ascending=False).head(10)
    fig = px.bar(data_frame=place_sum, x='장소', y='건수', color='장소')
    fig.update_layout(showlegend=False)   # [수업 외] 범례 숨기기 (x축에 이미 이름이 있으므로)
    st.plotly_chart(fig, use_container_width=True)

# [수업 외] st.expander : 눌러야 펼쳐지는 영역. 원본 표를 보고 싶은 사람만 열어 보게 한다.
with st.expander('표로 보기'):
    st.dataframe(type_sum[['범죄대분류', '범죄중분류', '전국']], hide_index=True)
