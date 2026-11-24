# =====================================================================
# common.py : 여러 페이지에서 같이 쓰는 함수 모음
#
# 주석 표시 규칙 (모든 파일 공통)
#   [수업 N장]  수업 시간에 배운 명령어를 그대로 쓴 부분
#   [수업 외]   수업에서 다루지 않은 코드. 무엇을 하는지, 왜 필요한지 자세히 설명
# =====================================================================

# [수업 4~6장] pandas, numpy 불러오기
import pandas as pd
import numpy as np

# [수업 11장] folium 지도
import folium

# [수업 외] 파일·인터넷 관련 기본 모듈 (파이썬에 기본으로 들어 있어 설치 필요 없음)
#   json            : 지도 경계 파일(GeoJSON)은 JSON 형식의 텍스트 → 파이썬 딕셔너리로 읽을 때 사용
#   os              : 파일이 이미 있는지 확인(os.path.exists), 경로 합치기(os.path.join)
#   urllib.request  : 인터넷 주소에서 파일을 내려받기(urlretrieve)
import json
import os
import urllib.request

# [수업 외] streamlit : 파이썬 코드만으로 웹사이트 화면을 만드는 패키지
#   st.title(), st.write() 처럼 한 줄씩 쓰면 그 순서대로 웹페이지에 표시된다.
#   실행: 터미널에서  streamlit run app.py   → 브라우저에 사이트가 열림
import streamlit as st


# [수업 외] 이 파일이 있는 폴더 위치
#   __file__ 은 "지금 실행 중인 파이썬 파일의 경로"를 뜻한다.
#   streamlit 을 어느 폴더에서 실행하든 data 폴더를 정확히 찾게 하려고 사용한다.
#   (수업처럼 pd.read_csv('data/...') 로 쓰면, 실행 위치가 다를 때 파일을 못 찾는다)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')


# ---------------------------------------------------------------------
# 1. 데이터 불러오기
# ---------------------------------------------------------------------

# [수업 외] @st.cache_data
#   함수 위에 붙이는 '데코레이터'. 처음 한 번만 함수를 실행하고 결과를 기억해 둔다.
#   streamlit 은 버튼을 누를 때마다 코드 전체를 처음부터 다시 실행하기 때문에,
#   이것을 붙이지 않으면 클릭할 때마다 CSV 를 다시 읽어서 사이트가 느려진다.
# [수업 외] data 폴더 안의 '경찰청_범죄 발생 지역별 통계_YYYY1231.csv' 파일들을 찾아 연도 목록을 만든다.
#   os.listdir(폴더) : 폴더 안의 파일 이름 목록
#   파일 이름 끝이 '20251231.csv' 이면 앞 4글자(2025)가 연도. 새 연도 CSV 를 넣으면 자동으로 선택지에 추가된다.
CRIME_PREFIX = '경찰청_범죄 발생 지역별 통계_'


def crime_years():
    years = []
    for name in os.listdir(DATA_DIR):
        if name.startswith(CRIME_PREFIX) and name.endswith('1231.csv'):
            years.append(int(name[len(CRIME_PREFIX):len(CRIME_PREFIX) + 4]))
    return sorted(years, reverse=True)   # 최신 연도가 맨 앞


@st.cache_data
def load_crime(year=2025):
    # [수업 4장] pd.read_csv
    #   경찰청 파일은 윈도우 한글 형식(cp949)으로 저장되어 있어 encoding 을 지정한다.
    #   장소별 통계는 2025년 파일만 있어서 연도와 상관없이 2025년을 쓴다.
    crime = pd.read_csv(os.path.join(DATA_DIR, f'{CRIME_PREFIX}{year}1231.csv'), encoding='cp949')
    place = pd.read_csv(os.path.join(DATA_DIR, '경찰청_범죄 발생 장소별 통계_20251231.csv'), encoding='cp949')
    return crime, place


@st.cache_data
def load_supports():
    return pd.read_csv(os.path.join(DATA_DIR, 'supports.csv'), encoding='cp949')


# AI 상담이 근거로 쓸 법률 조문 목록 (supports.csv 와 같은 방식)
@st.cache_data
def load_laws():
    return pd.read_csv(os.path.join(DATA_DIR, 'laws.csv'), encoding='cp949')


@st.cache_data
def load_population():
    gu = pd.read_csv(os.path.join(DATA_DIR, 'seoul_gu.csv'), encoding='cp949')
    sido = pd.read_csv(os.path.join(DATA_DIR, 'sido.csv'), encoding='cp949')
    return gu, sido


def filter_type(df, crime_type):
    # [수업 6장] 조건으로 행 고르기 (df[df['컬럼'] == 값])
    if crime_type == '전체':
        return df
    return df[df['범죄대분류'] == crime_type]


def region_columns(df):
    # [수업 외] 리스트 컴프리헨션 + startswith
    #   [c for c in 목록 if 조건] : 목록에서 조건에 맞는 것만 모아 새 리스트를 만든다.
    #   지역 컬럼 중 '외국 미국', '외국 중국' 같은 외국 컬럼은 국내 지도에 없으므로 뺀다.
    #   df.columns[2:] : 앞의 두 컬럼(범죄대분류, 범죄중분류)을 건너뛴 나머지 = 지역 컬럼
    return [c for c in df.columns[2:] if not c.startswith('외국')]


def add_grade(df):
    """인구가 있으면 '인구 10만 명당 건수', 없으면 '건수'를 값으로 쓰고 높음/보통/낮음 등급을 붙인다."""
    df = df.copy()   # [수업 5장] 원본을 바꾸지 않도록 복사

    # [수업 7장] isna() 로 빈 값 확인
    if df['인구'].isna().any():
        df['값'] = df['건수']
        unit = '발생 건수'
    else:
        df['값'] = df['건수'] / df['인구'] * 100000
        unit = '인구 10만 명당 발생 건수'

    # [수업 7장] quantile : 값을 작은 순으로 세웠을 때 33%, 66% 위치의 값
    q1 = df['값'].quantile(0.33)
    q2 = df['값'].quantile(0.66)
    # [수업 5장] np.where 중첩으로 등급 나누기
    df['등급'] = np.where(df['값'] >= q2, '높음', np.where(df['값'] >= q1, '보통', '낮음'))
    return df, unit


# 연도별 파일 형식이 달라서 지역 이름을 읽는 방법을 맞춰 준다.
#   2024~2025년 : '서울 종로구', '경기도 수원시'   (띄어쓰기 있음, 서울 구별 자료 있음)
#   2023년      : '서울종로구', '경기도수원시'     (띄어쓰기 없음, 서울 구별 자료 있음)
#   2018~2022년 : '서울', '부산', '세종', '경기 수원' (서울은 구별 자료 없이 합계만, 도는 일부 시만 있음)
METRO = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종시']   # 특별시·광역시·세종


def sido_name(col):
    """지역 컬럼 이름 → sido.csv 의 시도 이름. 시도를 정할 수 없으면 None"""
    _, sido_info = load_population()
    if col == '세종':                 # 2018~2022년 파일은 '세종시' 가 아니라 '세종'
        return '세종시'
    # [수업 외] startswith : 글자가 ~로 시작하는지 확인. 띄어쓰기가 있든 없든 앞부분으로 시도를 찾는다.
    for name in sido_info['시도']:
        if col.startswith(name):
            return name
    return None   # 예: 2018~2022년의 '경기 수원'(도 이름이 '경기' 라 안 맞음), '기타도시'


def has_gu_detail(year):
    """그 해 파일에 서울 자치구별 자료가 있는지 (2023년부터 있음)"""
    crime, _ = load_crime(year)
    return '서울' not in crime.columns


def seoul_table(crime_type, year=2025):
    """서울 자치구별 건수 표 (2023년 이후 파일만 가능)"""
    crime, _ = load_crime(year)
    data = filter_type(crime, crime_type)

    # [수업 외] 리스트 컴프리헨션 : '서울' 로 시작하는 컬럼만 고른다 (region_columns 설명 참고)
    seoul_cols = [c for c in data.columns if c.startswith('서울')]

    # [수업 외] sum() 의 결과(시리즈)를 reset_index() 로 표(데이터프레임)로 바꾼다.
    #   세로 방향 합계 → '서울 종로구: 123' 형태 → 컬럼 두 개(지역, 건수)짜리 표
    seoul = data[seoul_cols].sum().reset_index()
    seoul.columns = ['지역', '건수']
    # [수업 외] .str.replace : '서울 종로구'/'서울종로구' → '종로구' (지도 파일의 이름과 맞추기 위함)
    #   .str.strip() : 앞뒤 공백 제거
    seoul['구'] = seoul['지역'].str.replace('서울', '', n=1).str.strip()

    gu, _ = load_population()
    seoul = pd.merge(seoul, gu, on='구')   # [수업 6장] pd.merge 로 인구 합치기
    return add_grade(seoul)


def sido_table(crime_type, year=2025):
    """전국 시도별 건수 표. 2018~2022년은 특별시·광역시·세종만 정확히 계산할 수 있다."""
    crime, _ = load_crime(year)
    data = filter_type(crime, crime_type)

    total = data[region_columns(data)].sum().reset_index()
    total.columns = ['지역', '건수']
    total['시도'] = [sido_name(x) for x in total['지역']]

    # 2018~2022년 파일은 도 지역이 '경기 수원' 같은 일부 시만 있고 군 지역은 '도시이외' 로 묶여 있어
    # 도별 합계를 낼 수 없다. 그래서 특별시·광역시·세종만 남긴다. (지도에서 도는 회색)
    if not has_gu_detail(year):
        total = total[total['시도'].isin(METRO)]   # [수업 5장] isin

    # [수업 6장] groupby + agg 로 시도별 합계
    sido = total.groupby('시도', as_index=False).agg(건수=('건수', 'sum'))
    _, sido_info = load_population()
    sido = pd.merge(sido, sido_info, on='시도')
    return add_grade(sido)


def yearly_trend(crime_type):
    """연도별 전국 합계와 특별시·광역시별 건수 (모든 연도 파일에서 같은 기준으로 셀 수 있는 것만)"""
    rows = []
    for year in crime_years():
        crime, _ = load_crime(year)
        data = filter_type(crime, crime_type)
        cols = region_columns(data)
        rows.append({'연도': year, '지역': '전국', '건수': data[cols].sum().sum()})
        for col in cols:
            name = sido_name(col)
            if name in METRO:
                rows.append({'연도': year, '지역': name, '건수': data[col].sum()})
    trend = pd.DataFrame(rows)
    # 2023년 이후 파일은 한 시가 여러 구로 나뉘어 있으므로 시별로 다시 더한다.
    trend = trend.groupby(['연도', '지역'], as_index=False).agg(건수=('건수', 'sum'))
    return trend


# ---------------------------------------------------------------------
# 2. 지도
# ---------------------------------------------------------------------

# 구역 경계 파일 주소 (공개 저장소 southkorea-maps, 통계청 2013년 경계)
SEOUL_GEO_URL = 'https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json'
SIDO_GEO_URL = 'https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_provinces_geo_simple.json'


@st.cache_data
def load_geo(filename, url):
    # [수업 외] 경계 파일(GeoJSON) 준비
    #   GeoJSON : 각 구역(구, 시도)의 테두리 좌표를 담은 파일. folium 이 이걸 보고 구역 모양을 그린다.
    #   data 폴더에 없으면 처음 한 번 인터넷에서 내려받아 저장하고, 다음부터는 저장된 파일을 쓴다.
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        urllib.request.urlretrieve(url, path)
    # with open(...) as f : 파일을 열고, 블록이 끝나면 자동으로 닫아 준다.
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def make_choropleth(geo, df, key_col, legend, center, zoom):
    """값이 클수록 진하게 구역 전체를 칠하는 지도(단계 구분도)"""

    # [수업 11장] folium.Map : 지도 만들기 (location=[위도, 경도], zoom_start=확대 정도)
    #   배경 타일: 수업에서는 CARTO 키를 넣었지만, 키를 코드에 넣으면 GitHub 에 노출되므로
    #   키가 필요 없는 OpenStreetMap 기본 타일을 쓴다.
    m = folium.Map(location=center, zoom_start=zoom, tiles='OpenStreetMap')

    # [수업 외] 색 구간 나누기
    #   quantile([0, 0.2, ...]) : 값을 5등분하는 경계값. 강남구처럼 한 곳만 아주 커도 색이 고르게 나뉜다.
    #   set() 으로 같은 값(중복)을 없애고 sorted() 로 정렬한다. (경계값이 겹치면 folium 이 오류를 냄)
    bins = sorted(set(df['값'].quantile([0, 0.2, 0.4, 0.6, 0.8, 1]).tolist()))

    # [수업 외] folium.Choropleth : 구역을 값에 따라 색칠하는 지도
    #   geo_data   : 경계 파일
    #   data       : 값이 들어 있는 표,  columns=[이름 컬럼, 값 컬럼]
    #   key_on     : 경계 파일 안에서 이름이 들어 있는 위치 (feature → properties → name)
    #                표의 이름과 경계 파일의 이름이 같아야 색이 칠해진다.
    #   fill_color : 색 단계 이름. 'YlOrRd' = 노랑→주황→빨강
    ch = folium.Choropleth(
        geo_data=geo,
        data=df,
        columns=[key_col, '값'],
        key_on='feature.properties.name',
        bins=bins,
        fill_color='YlOrRd',
        fill_opacity=0.8,
        line_color='white',
        line_weight=1,
        nan_fill_color='lightgray',   # 값이 없는 구역은 회색
        legend_name=legend,
    )
    # [수업 외] 지도 위쪽 색 범례(숫자 막대) 숨기기
    #   구간 경계값이 붙어 있으면 숫자가 겹쳐 읽을 수 없어서 범례를 없앴다.
    #   대신 페이지 오른쪽 막대그래프와 마우스 툴팁으로 값을 확인한다.
    #   folium 은 범례를 Choropleth 안의 '자식 요소'(_children) 로 넣어 두는데, 이름이 'color_map' 으로 시작한다.
    #   그 이름의 자식만 지우면 범례가 빠진다. (list(...) 로 복사해 두고 지워야 반복 중 오류가 안 남)
    #   (범례를 다시 보고 싶으면 아래 for 문 세 줄을 지우면 된다)
    for key in list(ch._children):
        if key.startswith('color_map'):
            del ch._children[key]
    ch.add_to(m)

    # [수업 외] 마우스를 올리면 지역 이름과 값이 보이는 말풍선(툴팁)
    #   dict(zip(이름들, 값들)) : {'종로구': 123, '중구': 456, ...} 형태의 사전을 만든다.
    #   경계 파일의 각 구역(feature) 속성에 '값' 을 넣어 두고, GeoJsonTooltip 으로 보여 준다.
    value_dict = dict(zip(df[key_col], df['값']))
    for f in geo['features']:
        f['properties']['값'] = f"{value_dict.get(f['properties']['name'], 0):,.0f}"

    # style_function=lambda x: {...}
    #   lambda 는 이름 없는 짧은 함수. 모든 구역에 '투명(fillOpacity 0), 테두리 없음' 스타일을 준다.
    #   색은 위의 Choropleth 가 이미 칠했으므로, 이 층은 툴팁만 담당하게 투명하게 덮는다.
    folium.GeoJson(
        geo,
        style_function=lambda x: {'fillOpacity': 0, 'weight': 0},
        tooltip=folium.GeoJsonTooltip(fields=['name', '값'], aliases=['지역', '값']),
    ).add_to(m)
    return m


# ---------------------------------------------------------------------
# 3. 화면 공통 꾸미기
# ---------------------------------------------------------------------

def emergency_banner():
    # [수업 외] st.error : 빨간 상자로 강조된 글. 위급 상황 안내를 항상 맨 위에 보여 준다.
    st.error('**지금 위험하다면 바로 112** · 여성긴급전화 **1366** · 범죄피해자지원센터 **1577-1295**')
