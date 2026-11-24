# BigDataProject (re-main : 웹사이트 버전)

범죄 피해 유형을 확인하고 받을 수 있는 지원제도를 안내하며, 지역별 범죄 현황을 지도로 보여주는 프로젝트입니다.
`BigDataProject-main` 폴더의 노트북 버전을 웹사이트로 확장한 폴더입니다. 기존 폴더는 그대로 두었습니다.

## 웹사이트 버전 (Streamlit)
노트북과 같은 분석을 웹사이트로 옮긴 버전입니다. 수업에서 웹 화면 만드는 법은 배우지 않았기 때문에, 파이썬만으로 사이트를 만들 수 있는 **Streamlit**을 썼습니다. 화면 안의 분석·그래프·지도·AI 코드는 수업 내용(pandas, plotly, folium, OpenAI)을 그대로 씁니다.

```bash
pip install -r requirements.txt
streamlit run 홈.py
```
저장소 루트에서 바로 실행하려면 `streamlit run re-main/홈.py` 도 됩니다. 브라우저에서 http://localhost:8501 이 열립니다. AI 상담을 쓰려면 실행 전에 환경변수 `OPENAI_API_KEY` 를 설정하세요.

| 파일 | 화면 |
|---|---|
| `홈.py` | 첫 화면(복지로 구성 참고): 겪은 일 입력칸 → AI 상담, 상황별 바로 찾기 버튼, 메뉴 카드, 숫자 요약, 많이 찾은 상황 |
| `pages/1_내_상황_찾기.py` | 겪은 일을 체크하면 해당 지원제도를 카드로 보여줌 (구상 3번). 체크한 항목은 `data/interest_log.csv` 에 날짜와 함께 기록 (구상 5번, 개인정보 저장 안 함) |
| `pages/2_범죄_지도.py` | 서울 자치구 / 전국 시도 단계 구분도 + 막대그래프, **연도**·범죄 종류 선택 (구상 2번). 인구 10만 명당 건수로 표시 |
| `pages/3_범죄_통계.py` | 연도별 범죄 종류 TOP 10, 장소 TOP 10(2025년), 2018~2025년 연도별 추이 |
| `pages/4_AI_상담.py` | 상황을 글로 쓰면 OpenAI가 `laws.csv` 의 법률 조문을 근거로 해당할 수 있는 피해를 설명하고, `supports.csv` 안에서 지원제도를 안내 (구상 4번) |
| `common.py` | 여러 페이지에서 같이 쓰는 데이터 불러오기·지도 함수, 화면 꾸미기(CSS, 상단 긴급 연락처 띠, 카드) |
| `.streamlit/config.toml` | 사이트 색 설정 (흰 바탕 + 파란 강조색) |

**주석 표시 규칙**
- `[수업 N장]` 수업에서 배운 명령어를 그대로 쓴 부분
- `[수업 외]` 수업에서 다루지 않은 코드. 무엇을 하는지, 왜 필요한지 주석에 자세히 설명

수업 외로 쓴 주요 코드: Streamlit 화면 요소(`st.title`, `st.checkbox`, `st.selectbox`, `st.columns` 등), `@st.cache_data`, `st.session_state`, `streamlit_folium.st_folium`, `folium.Choropleth`·`GeoJsonTooltip`, `os.path`, `json`, `urllib.request`, 리스트 컴프리헨션, `sum(axis=1)`, `str.replace`·`split()`

## 구성 (노트북 버전)
- `범죄피해_지원_분석.ipynb` : 전체 코드 (위에서부터 순서대로 실행)
- `data/경찰청_범죄 발생 지역별 통계_YYYY1231.csv` (2018~2025년), `data/경찰청_범죄 발생 장소별 통계_20251231.csv` : 경찰청 범죄 통계
  - 새 연도 파일을 같은 이름 형식으로 넣으면 사이트의 연도 선택지에 자동으로 추가됩니다.
  - 2018~2022년 파일은 서울 자치구별 자료가 없고(서울 합계만), 도 지역은 일부 시만 나뉘어 있어 지도에서 특별시·광역시·세종만 표시합니다.
- `data/laws.csv` : AI 상담이 근거로 쓰는 법률 조문 목록 (국가법령정보센터 기준, 확인상태 '확인필요'는 law.go.kr 에서 재확인)
- `data/seoul_gu.csv`, `data/sido.csv` : 서울 자치구·시도 목록과 인구 (행정안전부 주민등록 인구, 2025년 12월 31일 기준. 다른 연도 지도에도 이 인구를 씀)
- `data/supports.csv` : 범죄피해 지원제도 목록 (확인상태 '확인필요'는 공식 자료로 재확인)

## 실행 방법
1. `pip install -r requirements.txt`
2. `data/seoul_gu.csv`, `data/sido.csv` 의 인구 칸 입력 (행정안전부 주민등록 인구통계, 2025년 12월 기준). 비우면 '발생 건수' 지도로 표시됩니다.
   (엑셀 저장 시 일반 'CSV' 형식 유지)
3. AI 상담에는 OpenAI API 키가 필요합니다. 아래 중 **하나만** 하면 됩니다. (키를 코드나 GitHub 에 올리지 마세요)
   - **가장 쉬운 방법**: `re-main` 폴더에 `.env` 파일을 만들고 `OPENAI_API_KEY=sk-...` 한 줄 저장 (`.gitignore` 에 있어 GitHub 에 안 올라감)
   - 환경변수: Windows PowerShell `$env:OPENAI_API_KEY="sk-..."` / 명령 프롬프트 `set OPENAI_API_KEY=sk-...` 를 **streamlit 을 실행할 그 터미널**에서 입력한 뒤 `streamlit run 홈.py`
   - Streamlit Cloud: 앱 설정 → Secrets 에 `OPENAI_API_KEY = "sk-..."`
   - 발표 현장용: AI 상담 페이지에 키를 직접 붙여 넣기 (저장되지 않음)
   - 키가 틀렸거나, 크레딧이 없거나, 모델 권한이 없으면 페이지에 이유가 한국어로 표시됩니다.
4. 노트북 실행. 지도 경계 파일은 처음 실행할 때 GitHub(southkorea-maps)에서 자동으로 내려받아 `data/seoul_geo.json`, `data/sido_geo.json` 으로 저장됩니다.
   - 내려받기에 실패하면: GitHub `southkorea/seoul-maps` → `kostat/2013/json` → `seoul_municipalities_geo_simple.json` 을 열고 Raw 내용을 `data/seoul_geo.json` 으로 저장, 시도는 `southkorea/southkorea-maps` → `kostat/2013/json` → `skorea_provinces_geo_simple.json` 을 `data/sido_geo.json` 으로 저장
   - 경계 파일 이름이 통계와 안 맞으면 노트북이 '지도에 없는 구/시도'를 출력합니다.
5. (선택) 배경 지도를 넣으려면 수업 11장의 xyzservices 키를 노트북의 `CARTO_KEY` 에 넣으세요. **GitHub에 올리기 전에 반드시 지우세요.**

## 노트북 내용
1. 전국 범죄 종류별·장소별 TOP 10 (plotly)
2. 서울 자치구 범죄 지도와 그래프 (구역 전체를 색으로 칠하는 단계 구분도 folium, plotly)
3. 전국 시도 범죄 지도 (같은 방식)
4. 피해 상황을 설명하면 지원제도를 안내하는 AI (OpenAI)

## 기존 구상 (원문)
1. csv 연동
2. 구상중 ( 범죄 카테고리별 지도 표시 광역시/지역별 세세하게 추후 상세추가)
3. 자신이 어떤일에 해당하는지 혹은 그냥 카테고리에 체크하고 그에 따른 페이지표시
4. 도움연결 / Ai를 통해 최근뉴스 및 관련법률 가져오기
5. 데이터베이스 연동시켜서 사용자가 어느걸 더 관심있어하는지도 체크( 추후 웹/앱의 업데이트에 사용자 친화적으로 혹은 사람들이 많이 찾는 메뉴로 집어넣을수도 있음 )
6. 사이트 혹은 앱의 UI디자인은 복지로 사이트를 참고하는게 좋다고 생각됨. 복잡하지않고 직관적인 사이트를 추구

### 수업에서 안 다룬 것
- `sum(axis=1)`, 리스트 컴프리헨션, `startswith()`·`split()`, `quantile()`
- 지도: `folium.Choropleth`(구역 칠하기), `folium.GeoJson` + 툴팁(`lambda`), 경계 파일(GeoJSON)과 `json`·`urllib.request`·`os.path`

### 현재 반영 상태
- 1번 csv 연동: 반영 (경찰청 CSV 2개)
- 2번 범죄 카테고리별 지도: 서울 자치구·전국 시도 단위 반영 (`crime_type` 변경). 시군구 단위 상세는 추후
- 3번 피해 유형 확인: 웹사이트 "내 상황 찾기" 체크리스트 + AI 상담
- 4번 도움 연결: 지원제도 목록 기반 안내 반영. 최근 뉴스·관련 법률 가져오기는 미반영
- 5번 관심 기록: 웹사이트 버전에서 CSV 기록으로 반영 (데이터베이스 연동은 추후)
- 6번 UI 디자인: 웹사이트 버전에서 복지로처럼 첫 화면 메뉴 카드 구성
