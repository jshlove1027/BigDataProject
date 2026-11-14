# 범죄율 지도 (서울 · 전국)

## 준비물 (data/ 폴더)
1. `crime.csv` — 경찰청_범죄_발생_지역별_통계_20251231.csv (이미 들어있음)
2. `sigungu.geojson` — 시군구 경계 GeoJSON. southkorea-maps 저장소의 kostat/2018/json 폴더에서 시군구(municipalities) GeoJSON(`...geo...json`)을 받으세요. 속성에 `code`(숫자 코드)와 `name`이 있어야 합니다.
3. `population.csv` — 행정안전부 주민등록 인구통계(jumin.mois.go.kr), 2025년 12월 기준, 시군구 단위까지 조회해 CSV로 저장 (첫 컬럼 행정구역명, '총인구수' 컬럼 포함)

## 실행
```bash
pip install -r requirements.txt
python make_maps.py --geo data/sigungu.geojson --pop data/population.csv
```
인구 파일이 아직 없으면 `--pop` 을 빼고 실행하면 '발생 건수' 지도로 먼저 확인할 수 있습니다.
범죄 유형은 `--types 전체 폭력범죄 사기` 처럼 지정합니다 (범죄대분류·중분류 이름).

## 결과 (out/)
`map_national_*.png`, `map_seoul_*.png`, `rank_*.csv`(지역별 순위)

## 주의
- 첫 실행 때 "[매칭]" 줄에 나오는 지도에 값이 없는 지역 / 통계에서 못 찾은 지역을 꼭 확인하세요.
- 2018 경계와 2025 통계의 행정구역 차이는 `make_maps.py` 의 ALIAS 에 추가하면 됩니다.
- 범죄율은 주민등록 인구 기준이라 유동인구가 많은 지역(서울 중구·종로구 등)은 높게 나올 수 있습니다.
