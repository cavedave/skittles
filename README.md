# Skittles color analysis

Reproduce the charts with Python 3.11+ (or 3.13).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 1. Fun-size bags (Clare Wallace data)

- **Data:** `skittles-megalist-3-6-25.xlsx` (sheet `Basic data`)
- **Script:** `skittles_analysis.py`
- **Output:** `skittles_chart_v10.png` (rainbow stack + sort by total per bag)

```bash
python skittles_analysis.py
```

Keeps bags with **15–18** Skittles; drops obvious outliers. Bars stack **R→O→Y→G→P**; rows sorted by **total Skittles per bag** (largest first), then by those five counts. Duplicate packs marked on the left. Older charts: `skittles_chart_v9.png` etc.

## 2. Full-size packs (possibly-wrong dataset)

- **Data:** `skittles_possiblywrong.txt` (tab-separated; from [possibly-wrong/skittles](https://github.com/possibly-wrong/skittles))
- **Script:** `skittles_possiblywrong_analysis.py`
- **Cleaning:** Drops **2** outlier packs (totals **45** and **73**); keeps **54–65** Skittles per pack (**466** packs).
- **Bar order:** Red → Orange → Yellow → Green → Purple (ROYGBV-style; no blue in Skittles).

```bash
python skittles_possiblywrong_analysis.py
```

### Sort modes

Edit `SORT_MODE` at the top of `skittles_possiblywrong_analysis.py`:

| `SORT_MODE`           | Effect                                      | Output file                          |
|-----------------------|---------------------------------------------|--------------------------------------|
| `total_then_rainbow`  | Largest pack first, then rainbow tie-break  | `skittles_possiblywrong_chart_v4.png` |
| `rainbow_count`       | Sort by red, then orange, …                 | `skittles_possiblywrong_chart_v3.png` |

### Refresh data from upstream

```bash
curl -o skittles_possiblywrong.txt \
  https://raw.githubusercontent.com/possibly-wrong/skittles/master/skittles.txt
```

## Chart versions on disk

**Fun-size (Wallace):** `skittles_chart.png` … `skittles_chart_v10.png` — **v10** matches `skittles_analysis.py`.

**Full-size:** `skittles_possiblywrong_chart.png` (all 468, no outlier removal), **v2** (outliers removed, old sort), **v3** / **v4** (rainbow stack; v3 vs v4 = sort mode above).

## Repo

Pushed to **https://github.com/cavedave/skittles** — clone, install deps, run scripts as above.
