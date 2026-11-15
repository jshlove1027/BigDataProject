# =====================================================================
# AI 상담 : 겪은 일을 글로 쓰면 AI 가 지원제도 목록 안에서 안내 (README 4번)
#   수업 10주차(OpenAI)의 client.responses.create 방식을 그대로 사용한다.
# 주석 표시 규칙: [수업 N장] 수업에서 배운 코드 / [수업 외] 수업에서 안 배운 코드(자세히 설명)
# =====================================================================

import os
import streamlit as st
from common import load_supports, emergency_banner

st.set_page_config(page_title='AI 상담', layout='wide')
st.title('AI 상담')
emergency_banner()

MODEL = 'gpt-5.6-luna'   # [수업 10주차] 수업에서 사용한 모델. 사용할 수 있는 다른 모델로 바꿔도 된다.

st.write('겪은 일을 적어 주시면 받을 수 있는 지원제도를 안내해 드립니다.')
st.warning('입력한 내용은 외부 AI 서비스(OpenAI)로 전송됩니다. 이름·주소·전화번호 같은 개인정보는 쓰지 마세요.')

# [수업 10주차] API 키는 환경변수 OPENAI_API_KEY 에서 읽는다. (코드나 GitHub 에 키를 쓰지 않기)
# [수업 외] os.environ.get : 환경변수가 없으면 오류 대신 None 을 돌려준다 (수업의 os.environ[...] 는 없으면 오류)
if os.environ.get('OPENAI_API_KEY') is None:
    st.info('AI 상담을 쓰려면 환경변수 OPENAI_API_KEY 를 설정한 뒤 사이트를 다시 실행하세요. (README 참고)')
    st.stop()

# [수업 외] st.text_area : 여러 줄 입력칸 / st.button : 누르면 True
story = st.text_area('어떤 일이 있었나요?', height=150,
                     placeholder='예) 모르는 번호로 온 문자의 링크를 눌렀는데, 조금 뒤 계좌에서 돈이 빠져나갔어요.')

if st.button('안내 받기', type='primary'):
    if story.strip() == '':   # [수업 외] strip() : 앞뒤 공백 제거. 빈 칸으로 누른 경우를 막는다.
        st.error('내용을 입력해 주세요.')
        st.stop()

    supports = load_supports()

    # [수업 10주차] 분석 결과(표)를 to_string() 으로 글자로 바꿔 prompt 안에 넣는 방식
    prompt = f"""
당신은 범죄 피해자에게 받을 수 있는 지원제도를 안내하는 도우미입니다.

[피해자가 설명한 상황]
{story}

[안내할 수 있는 지원제도 목록]
{supports.to_string()}

다음 규칙을 지켜 안내해주세요.
1. 위 목록에 있는 제도만 안내하고, 목록에 없는 제도·금액·기한은 지어내지 마세요.
2. 먼저 어떤 유형의 피해일 수 있는지 한두 문장으로 설명하세요. 확정하지 말고 '~일 수 있습니다'라고 쓰세요.
3. 신체 위험이 있거나 급박해 보이면 가장 먼저 112 신고를 안내하세요.
4. 해당할 수 있는 제도를 '제도명 - 하는 일 - 연락처' 순서로 정리하세요.
5. 확인상태가 '확인필요'인 제도는 공식 기관에 다시 확인하라고 덧붙이세요.
6. 마지막에 '법률 자문이 아닌 참고용 안내입니다'라고 쓰세요.
"""

    # [수업 10주차] OpenAI 객체를 만들고 질문 보내기
    from openai import OpenAI
    client = OpenAI()

    # [수업 외] st.spinner : 기다리는 동안 '안내를 만드는 중' 표시
    with st.spinner('안내를 만드는 중입니다...'):
        # [수업 10주차] 수업처럼 try/except 로 오류가 나도 사이트가 멈추지 않게 한다.
        try:
            response = client.responses.create(model=MODEL, input=prompt)
            st.markdown(response.output_text)   # [수업 외] st.markdown : 굵게·목록 같은 서식을 살려 표시
        except Exception as e:
            st.error(f'AI 응답을 받지 못했습니다: {type(e).__name__} {e}')
