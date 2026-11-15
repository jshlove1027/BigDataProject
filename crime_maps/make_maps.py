"""경찰청 범죄 발생 지역별 통계 + 주민등록 인구 + 시군구 경계(GeoJSON) -> 범죄율 지도(PNG)

실행 예
  python make_maps.py --crime data/crime.csv --geo data/sigungu.geojson --pop data/population.csv
  (--pop 을 빼면 인구 보정 없이 '발생 건수' 지도를 그립니다)
  python make_maps.py ... --types 전체 폭력범죄 사기      # 범죄대분류·중분류 이름도 가능

결과: out/ 폴더에 전국·서울 지도 PNG 와 순위 CSV
"""
import argparse, json, re
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath

plt.rcParams["font.family"] = ["Malgun Gothic", "AppleGothic", "NanumGothic", "Noto Sans CJK KR", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

SIDO_CODE = {"11": "서울", "21": "부산", "22": "대구", "23": "인천", "24": "광주", "25": "대전", "26": "울산", "29": "세종",
             "31": "경기", "32": "강원", "33": "충북", "34": "충남", "35": "전북", "36": "전남", "37": "경북", "38": "경남", "39": "제주"}
SIDO_PREFIX = {"서울": "서울", "부산": "부산", "대구": "대구", "인천": "인천", "광주": "광주", "대전": "대전", "울산": "울산",
               "세종시": "세종", "경기도": "경기", "강원도": "강원", "충북": "충북", "충남": "충남", "전북": "전북",
               "전남": "전남", "경북": "경북", "경남": "경남", "제주": "제주"}
FULL = {"서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구", "인천광역시": "인천", "광주광역시": "광주",
        "대전광역시": "대전", "울산광역시": "울산", "세종특별자치시": "세종", "경기도": "경기", "강원도": "강원",
        "강원특별자치도": "강원", "충청북도": "충북", "충청남도": "충남", "전라북도": "전북", "전북특별자치도": "전북",
        "전라남도": "전남", "경상북도": "경북", "경상남도": "경남", "제주특별자치도": "제주"}
# 경계 파일의 옛 이름 -> 통계 파일 이름  (시도, 경계파일 이름): 통계 이름
ALIAS = {("인천", "남구"): "미추홀구", ("부산", "부산진구"): "진구"}


def read_csv(path):
    for enc in ("utf-8-sig", "cp949"):
        try:
            return pd.read_csv(path, encoding=enc, dtype=str)
        except UnicodeDecodeError:
            continue
    raise SystemExit(f"인코딩을 읽을 수 없습니다: {path}")


def to_num(s):
    return pd.to_numeric(s.astype(str).str.replace(",", "").str.strip(), errors="coerce")


# ---------------------------------------------------------------- 범죄 통계
def load_crime(path, types):
    df = read_csv(path)
    df.columns = [str(c).strip() for c in df.columns]
    big, mid = "범죄대분류", "범죄중분류"
    df[big] = df[big].ffill()
    keys = {}
    for c in df.columns[2:]:
        t = c.split()
        if t[0] in SIDO_PREFIX:
            keys[c] = (SIDO_PREFIX[t[0]], "세종시" if t[0] == "세종시" else "".join(t[1:]))
        elif t[0] != "외국":
            print(f"[경고] 지역으로 분류하지 못한 컬럼(제외): {c}")
    num = df[list(keys)].apply(to_num).fillna(0)
    tables = {}
    for ty in types:
        if ty == "전체":
            mask = pd.Series(True, index=df.index)
        elif ty in set(df[big]):
            mask = df[big] == ty
        elif ty in set(df[mid]):
            mask = df[mid] == ty
        else:
            raise SystemExit(f"'{ty}' 는 범죄대분류/중분류에 없습니다. 예: 전체, 강력범죄, 폭력범죄, 절도범죄, 지능범죄, 사기, 폭행")
        s = num[mask].sum()
        tables[ty] = pd.DataFrame({"sido": [k[0] for k in keys.values()], "sigungu": [k[1] for k in keys.values()],
                                   "count": s.values})
    return tables


# ---------------------------------------------------------------- 인구
def load_pop(path, col=None):
    df = read_csv(path)
    df.columns = [str(c).strip() for c in df.columns]
    name_col = df.columns[0]
    col = col or next((c for c in df.columns[1:] if "총인구" in c), None) \
        or next((c for c in df.columns[1:] if to_num(df[c]).notna().mean() > 0.8), None)
    if col is None:
        raise SystemExit(f"인구 컬럼을 찾지 못했습니다. --pop-col 로 지정하세요. 컬럼: {list(df.columns)}")
    print(f"[인구] 사용 컬럼: {col}")
    rows = []
    for name, val in zip(df[name_col], to_num(df[col])):
        tok = re.sub(r"\(.*?\)", "", str(name)).split()
        if not tok or pd.isna(val) or tok[0] not in FULL:
            continue
        sido = FULL[tok[0]]
        if sido == "세종" and len(tok) == 1:
            rows.append((sido, "세종시", val))
        elif len(tok) == 2 and not re.match(r"^.+?시.+구$", tok[1]):   # 시도 합계·시 아래 구 행은 제외
            rows.append((sido, ALIAS.get((sido, tok[1]), tok[1]), val))
    return pd.DataFrame(rows, columns=["sido", "sigungu", "population"])


# ---------------------------------------------------------------- 경계
def path_of(geom):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    verts, codes = [], []
    for poly in polys:
        for ring in poly:
            ring = np.asarray(ring, dtype=float)[:, :2]
            c = np.full(len(ring), MPath.LINETO)
            c[0], c[-1] = MPath.MOVETO, MPath.CLOSEPOLY
            verts.append(ring)
            codes.append(c)
    return MPath(np.concatenate(verts), np.concatenate(codes))


def load_geo(path):
    g = json.load(open(path, encoding="utf-8"))
    if g.get("type") != "FeatureCollection":
        raise SystemExit("GeoJSON(FeatureCollection) 파일이 필요합니다. TopoJSON 이면 ...-geo.json 쪽을 받으세요.")
    feats = []
    for f in g["features"]:
        p = f["properties"]
        sido = SIDO_CODE.get(str(p.get("code", ""))[:2])
        if sido is None:
            continue
        name = re.sub(r"\s+", "", str(p.get("name", "")))
        m = re.match(r"^(.+?시)(.+구)$", name)          # 수원시장안구 -> 수원시 (통계가 시 단위라서)
        if m:
            name = m.group(1)
        name = "세종시" if sido == "세종" else ALIAS.get((sido, name), name)
        feats.append({"sido": sido, "sigungu": name, "path": path_of(f["geometry"])})
    return feats


def attach(feats, table):
    val = {(r.sido, r.sigungu): r.value for r in table.itertuples() if not np.isnan(r.value)}
    used = set()
    for f in feats:
        f["value"] = val.get((f["sido"], f["sigungu"]), np.nan)
        if not np.isnan(f["value"]):
            used.add((f["sido"], f["sigungu"]))
    by_name = defaultdict(list)
    for k in val:
        if k not in used:
            by_name[k[1]].append(k)
    for f in feats:                      # 소속 시도가 바뀐 곳(예: 군위군)은 이름만으로 한 번 더 매칭
        if np.isnan(f["value"]) and len(by_name.get(f["sigungu"], [])) == 1:
            k = by_name[f["sigungu"]][0]
            f["value"] = val[k]
            used.add(k)
    miss_geo = sorted({f"{f['sido']} {f['sigungu']}" for f in feats if np.isnan(f["value"])})
    miss_tab = sorted(f"{k[0]} {k[1]}" for k in val if k not in used)
    return miss_geo, miss_tab


# ---------------------------------------------------------------- 그리기
def draw(feats, title, label, out_png, annotate=False):
    vals = np.array([f["value"] for f in feats if not np.isnan(f["value"])])
    bins = np.unique(np.quantile(vals, np.linspace(0, 1, 6)))
    cmap = ListedColormap(plt.get_cmap("YlOrRd")(np.linspace(0.12, 0.95, len(bins) - 1)))
    norm = BoundaryNorm(bins, cmap.N)
    fig, ax = plt.subplots(figsize=(10, 10) if annotate else (8, 10))
    allv = []
    for f in feats:
        v = f["value"]
        face = "#d9d9d9" if np.isnan(v) else cmap(norm(v))
        ax.add_patch(PathPatch(f["path"], facecolor=face, edgecolor="white", linewidth=0.3))
        allv.append(f["path"].vertices)
        if annotate and not np.isnan(v):
            lo, hi = f["path"].vertices.min(0), f["path"].vertices.max(0)
            ax.text((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, f"{f['sigungu']}\n{v:,.0f}", ha="center", va="center", fontsize=7)
    pts = np.concatenate(allv)
    ax.set_xlim(pts[:, 0].min(), pts[:, 0].max())
    ax.set_ylim(pts[:, 1].min(), pts[:, 1].max())
    ax.set_aspect(1 / np.cos(np.radians(pts[:, 1].mean())))
    ax.axis("off")
    ax.set_title(title, fontsize=14)
    cb = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax, shrink=0.55, ticks=bins)
    cb.ax.set_yticklabels([f"{b:,.0f}" for b in bins])
    cb.set_label(label)
    fig.savefig(out_png, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crime", default="data/crime.csv")
    ap.add_argument("--geo", default="data/sigungu.geojson", help="시군구 경계 GeoJSON")
    ap.add_argument("--pop", default="data/population.csv",help="시군구별 주민등록 인구 CSV (없으면 발생 건수 지도)")
    ap.add_argument("--pop-col")
    ap.add_argument("--types", nargs="+", default=["전체", "강력범죄", "폭력범죄", "절도범죄", "지능범죄"])
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(exist_ok=True)

    tables = load_crime(a.crime, a.types)
    pop = load_pop(a.pop, a.pop_col) if a.pop else None
    feats = load_geo(a.geo)
    label = "인구 10만 명당 발생 건수" if pop is not None else "발생 건수"

    for ty, t in tables.items():
        if pop is not None:
            t = t.merge(pop, on=["sido", "sigungu"], how="left")
            if t.population.isna().any():
                print(f"[경고:{ty}] 인구 매칭 실패: {sorted(t[t.population.isna()].sigungu)}")
            t["value"] = t["count"] / t["population"] * 1e5
        else:
            t["value"] = t["count"].astype(float)
        miss_geo, miss_tab = attach(feats, t)
        if ty == list(tables)[0]:
            print(f"[매칭] 지도에 값이 없는 지역: {miss_geo}\n[매칭] 지도에서 못 찾은 통계 지역: {miss_tab}")
        safe = re.sub(r"[^\w가-힣]+", "_", ty)
        t.sort_values("value", ascending=False).to_csv(out / f"rank_{safe}.csv", index=False, encoding="utf-8-sig")
        draw(feats, f"전국 시군구 {ty} {label} (2025)", label, out / f"map_national_{safe}.png")
        draw([f for f in feats if f["sido"] == "서울"], f"서울 자치구 {ty} {label} (2025)", label,
             out / f"map_seoul_{safe}.png", annotate=True)
        print(f"[완료] {ty}")


if __name__ == "__main__":
    main()
