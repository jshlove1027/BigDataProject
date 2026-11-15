# BigDataProject

범죄 피해 유형을 확인하고 받을 수 있는 지원제도를 안내하며, 지역별 범죄 현황을 지도로 보여주는 프로젝트입니다.
수업 시간에 배운 내용(pandas, plotly, folium, OpenAI)으로 만든 주피터 노트북 버전입니다.

## 구성
- `범죄피해_지원_분석.ipynb` : 전체 코드 (위에서부터 순서대로 실행)
- `data/경찰청_범죄 발생 지역별 통계_20251231.csv`, `data/경찰청_범죄 발생 장소별 통계_20251231.csv` : 경찰청 범죄 통계
- `data/seoul_gu.csv`, `data/sido.csv` : 서울 자치구·시도 목록과 **인구 칸(직접 입력)**
- `data/supports.csv` : 범죄피해 지원제도 목록 (확인상태 '확인필요'는 공식 자료로 재확인)

## 실행 방법
1. `pip install -r requirements.txt`
2. `data/seoul_gu.csv`, `data/sido.csv` 의 인구 칸 입력 (행정안전부 주민등록 인구통계, 2025년 12월 기준). 비우면 '발생 건수' 지도로 표시됩니다.
   (엑셀 저장 시 일반 'CSV' 형식 유지)
3. AI 안내 부분은 환경변수 `OPENAI_API_KEY` 필요 (키를 코드나 저장소에 올리지 마세요)
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
- 3번 피해 유형 확인: AI가 상황 설명을 읽고 해당 유형 안내 (체크리스트 화면은 미반영)
- 4번 도움 연결: 지원제도 목록 기반 안내 반영. 최근 뉴스·관련 법률 가져오기는 미반영
- 5번 데이터베이스, 6번 UI 디자인: 미반영 (웹/앱으로 확장할 때 진행)
