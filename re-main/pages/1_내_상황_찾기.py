# =====================================================================
# 내 상황 찾기 : 겪은 일을 체크하면 해당하는 지원제도를 보여 주는 페이지 (README 3번)
# 주석 표시 규칙: [수업 N장] 수업에서 배운 코드 / [수업 외] 수업에서 안 배운 코드(자세히 설명)
# =====================================================================

import streamlit as st
import pandas as pd
import os
from datetime import date   # [수업 외] 오늘 날짜를 구하는 파이썬 기본 모듈 (기록에 날짜를 남기려고 사용)
from common import load_supports, emergency_banner, DATA_DIR

st.set_page_config(page_title='내 상황 찾기', layout='wide')
st.title('내 상황 찾기')
emergency_banner()

# 상황 → 안내할 제도명 목록 (제도명은 data/supports.csv 의 '제도명' 과 똑같이 써야 한다)
# [수업 외] 딕셔너리 { 키: 값 } 에 리스트를 값으로 넣은 형태
SITUATIONS = {
    '폭행·상해를 당했어요': ['범죄피해자지원센터', '스마일센터', '대한법률구조공단'],
    '성범죄 피해를 입었어요': ['여성긴급전화 1366', '해바라기센터', '스마일센터', '범죄피해자지원센터'],
    '가정폭력을 겪고 있어요': ['여성긴급전화 1366', '해바라기센터', '범죄피해자지원센터'],
    '불법촬영·유포(협박)를 당했어요': ['디지털성범죄피해자지원센터', '여성긴급전화 1366'],
    '누군가 계속 따라오거나 연락해요(스토킹)': ['스토킹 피해자 보호 조치', '여성긴급전화 1366'],
    '보이스피싱·사기를 당했어요': ['보이스피싱 지급정지·피해구제', '대한법률구조공단', '범죄피해자지원센터'],
    '물건을 도난당했어요': ['범죄피해자지원센터', '대한법률구조공단'],
    '크게 다쳤거나 가족을 잃었어요': ['범죄피해구조금', '범죄피해자지원센터', '스마일센터'],
}

st.write('해당하는 것을 모두 체크하세요. (여러 개 선택 가능)')

# [수업 외] st.checkbox(글자) : 체크박스. 체크하면 True, 아니면 False 를 돌려준다.
#   for 문으로 상황마다 체크박스를 만들고, 체크된 것만 checked 리스트에 모은다.
checked = []
for s in SITUATIONS:
    if st.checkbox(s):
        checked.append(s)

if len(checked) == 0:
    st.info('위에서 상황을 하나 이상 체크해 주세요.')
    st.stop()   # [수업 외] st.stop() : 여기서 페이지 그리기를 멈춘다 (아래 내용은 보이지 않음)

# 체크한 상황들의 제도명을 모은다 (중복 제거, 순서 유지)
names = []
for s in checked:
    for n in SITUATIONS[s]:
        if n not in names:
            names.append(n)

supports = load_supports()
# [수업 5장] isin : 목록에 들어 있는 행만 고르기
result = supports[supports['제도명'].isin(names)]

st.subheader(f'받을 수 있는 지원 {len(result)}가지')

# [수업 외] iterrows() : 표를 한 행씩 꺼내는 반복문. row['컬럼'] 으로 그 행의 값을 쓴다.
# [수업 외] st.container(border=True) : 테두리가 있는 카드 모양 상자
for _, row in result.iterrows():
    with st.container(border=True):
        st.markdown(f"### {row['제도명']}")
        st.write(row['하는일'])
        st.markdown(f"**연락처** : {row['연락처']}")
        st.caption(f"대상 : {row['대상피해']} · {row['확인상태']}")
        if row['확인상태'] == '확인필요':
            st.warning('이 제도는 내용이 바뀌었을 수 있습니다. 해당 기관에 다시 확인하세요.')

st.page_link('pages/4_AI_상담.py', label='내 상황을 글로 자세히 설명하고 AI 안내 받기 →')


# ---------------------------------------------------------------------
# 관심 기록 남기기 (README 5번) : 어떤 상황이 많이 선택되는지 data/interest_log.csv 에 쌓는다.
#   날짜와 상황 이름만 저장하고 개인정보는 저장하지 않는다.
#   (실제 서비스로 키울 때는 CSV 대신 데이터베이스로 바꾸면 된다)
# ---------------------------------------------------------------------
# [수업 외] st.session_state : 사용자가 페이지에 있는 동안 값을 기억하는 저장소.
#   streamlit 은 체크할 때마다 코드를 처음부터 다시 실행하므로, 이미 기록한 상황을
#   기억해 두지 않으면 같은 체크가 계속 중복 기록된다.
if 'logged' not in st.session_state:
    st.session_state['logged'] = []

new = [s for s in checked if s not in st.session_state['logged']]   # [수업 외] 리스트 컴프리헨션
if len(new) > 0:
    log_path = os.path.join(DATA_DIR, 'interest_log.csv')
    new_log = pd.DataFrame({'날짜': str(date.today()), '상황': new})   # [수업 4장] 데이터 프레임 만들기
    if os.path.exists(log_path):
        new_log = pd.concat([pd.read_csv(log_path), new_log])        # [수업 6장] pd.concat 으로 이어 붙이기
    new_log.to_csv(log_path, index=False)   # [수업 외] to_csv : 표를 CSV 파일로 저장 (index=False: 행 번호 제외)
    st.session_state['logged'] += new
