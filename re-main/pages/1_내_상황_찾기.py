# =====================================================================
# 내 상황 찾기 : 겪은 일을 체크하면 해당하는 지원제도를 보여 주는 페이지 (README 3번)
# 주석 표시 규칙: [수업 N장] 수업에서 배운 코드 / [수업 외] 수업에서 안 배운 코드(자세히 설명)
# =====================================================================

import streamlit as st
import pandas as pd
import os
from datetime import date   # [수업 외] 오늘 날짜를 구하는 파이썬 기본 모듈 (기록에 날짜를 남기려고 사용)
from common import (load_supports, load_laws, page_setup, section, support_card, footer,
                    SITUATIONS, SITUATION_LAWS, DATA_DIR)

page_setup('내 상황 찾기', '해당하는 상황을 모두 체크하세요. 받을 수 있는 지원제도와 관련 법률을 함께 보여 드립니다.')

# 홈에서 '상황별로 바로 찾기' 버튼을 누르고 왔다면 그 상황을 미리 체크해 둔다.
# [수업 외] st.session_state.pop(이름, 기본값) : 저장된 값을 꺼내면서 지운다 (한 번만 쓰고 없앰)
preselect = st.session_state.pop('preselect', None)

# [수업 외] st.checkbox(글자, value=처음 상태) : 체크하면 True, 아니면 False 를 돌려준다.
#   상황 8개를 2칸으로 나눠 배치하고, 체크된 것만 checked 리스트에 모은다.
checked = []
with st.container(border=True):
    cols = st.columns(2)
    for i, s in enumerate(SITUATIONS):   # [수업 외] enumerate : 순서 번호(i)와 값을 같이 꺼낸다
        with cols[i % 2]:
            if st.checkbox(s, value=(s == preselect)):
                checked.append(s)

if len(checked) == 0:
    st.info('위에서 상황을 하나 이상 체크해 주세요.')
    footer()
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

section(f'받을 수 있는 지원 {len(result)}가지')

# [수업 외] iterrows() : 표를 한 행씩 꺼내는 반복문. row['컬럼'] 으로 그 행의 값을 쓴다.
#   support_card(row) : common.py 의 카드 모양 함수 (제도명, 대상, 확인상태, 하는 일, 연락처)
cols = st.columns(2)
for i, (_, row) in enumerate(result.iterrows()):
    with cols[i % 2]:
        support_card(row)

# 관련 법률 : 체크한 상황과 연결된 조문을 data/laws.csv 에서 골라 보여 준다
section('관련 법률 근거')
types = []
for s in checked:
    types += SITUATION_LAWS[s]
laws = load_laws()
law_rows = laws[laws['피해유형'].isin(types)]   # [수업 5장] isin
for _, row in law_rows.iterrows():
    # [수업 외] st.expander : 눌러야 펼쳐지는 상자
    with st.expander(f"{row['죄명']} · 「{row['법률']}」 {row['조문']}"):
        st.write(f"**성립 요건** : {row['성립요건']}")
        st.write(f"**법정형** : {row['법정형']}")
        if isinstance(row['참고'], str):   # [수업 외] 참고 칸이 비어 있으면(NaN) 건너뛴다
            st.write(f"**참고** : {row['참고']}")
st.caption('해당 여부는 구체적인 사실에 따라 달라집니다. 실제 판단은 대한법률구조공단(132)이나 변호사와 상담하세요.')

with st.container(border=True):
    st.page_link('pages/4_AI_상담.py', label='내 상황을 글로 자세히 설명하고 AI 안내 받기', icon=':material/forum:')


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

footer()
