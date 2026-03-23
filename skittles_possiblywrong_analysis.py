"""
Skittles Analysis — Possibly Wrong dataset
-------------------------------------------
Analyzes 468 full-size Skittles packs from the possibly-wrong dataset.
Same chart style as the Clare Wallace fun-size analysis.

Source: https://github.com/possibly-wrong/skittles

Usage:
    pip install pandas matplotlib
    python skittles_possiblywrong_analysis.py

Sort modes (change SORT_MODE below):
    total_then_rainbow — sort by pack size, then R→O→Y→G→P (chart v4)
    rainbow_count      — sort by red, then orange, … (chart v3)
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter

# Recreate v4 (recommended) or v3: change this and re-run.
SORT_MODE = "total_then_rainbow"  # or "rainbow_count"

# ── 1. LOAD ───────────────────────────────────────────────────────────────────

DATA_FILE = "skittles_possiblywrong.txt"

df = pd.read_csv(DATA_FILE, sep="\t")
df = df.drop(columns=["Uncounted"])
df.columns = ["red", "orange", "yellow", "green", "purple"]

print(f"Loaded: {len(df)} packs")

# ── 2. CLEAN & STATS ─────────────────────────────────────────────────────────

totals = df.sum(axis=1)
print(f"Before cleaning: min={totals.min()}, max={totals.max()}, mean={totals.mean():.1f}")

MIN_SKITTLES = 54
MAX_SKITTLES = 65
outliers = df[~totals.between(MIN_SKITTLES, MAX_SKITTLES)]
df = df[totals.between(MIN_SKITTLES, MAX_SKITTLES)].reset_index(drop=True)
print(f"Removed {len(outliers)} outlier packs (totals: {sorted(outliers.sum(axis=1).tolist())})")

totals = df.sum(axis=1)
print(f"Clean dataset: {len(df)} packs, min={totals.min()}, max={totals.max()}, mean={totals.mean():.1f}")

# ── 3. PREPARE ────────────────────────────────────────────────────────────────

COLORS = ["red", "orange", "yellow", "green", "purple"]

COLOR_HEX = {
    "red":    "#c0043f",
    "orange": "#e64808",
    "yellow": "#f1be02",
    "green":  "#048207",
    "purple": "#441349",
}

color_order = ["red", "orange", "yellow", "green", "purple"]
print(f"Colour order (rainbow): {color_order}")
print(f"Sort mode: {SORT_MODE}")

if SORT_MODE == "total_then_rainbow":
    sorted_indices = sorted(
        range(len(df)),
        key=lambda i: [df.loc[i, color_order].sum()] + [df.loc[i, c] for c in color_order],
        reverse=True,
    )
    chart_version = "v4"
elif SORT_MODE == "rainbow_count":
    sorted_indices = sorted(
        range(len(df)),
        key=lambda i: [df.loc[i, c] for c in color_order],
        reverse=True,
    )
    chart_version = "v3"
else:
    raise ValueError(f"Unknown SORT_MODE: {SORT_MODE!r} (use total_then_rainbow or rainbow_count)")

df_sorted = df.iloc[sorted_indices].reset_index(drop=True)

bag_tuples = [tuple(row) for row in df_sorted[color_order].values.tolist()]
counts = Counter(bag_tuples)
is_duplicate = [counts[t] > 1 for t in bag_tuples]
n_dupes = sum(is_duplicate)
n_unique = len(df_sorted) - n_dupes

print(f"Duplicates: {n_dupes} of {len(df_sorted)} packs")

# ── 4. PLOT ───────────────────────────────────────────────────────────────────

n_bags = len(df_sorted)

bag_to_group = {}
group_id = 0
tuple_to_group = {}
for i, t in enumerate(bag_tuples):
    if counts[t] > 1:
        if t not in tuple_to_group:
            tuple_to_group[t] = group_id
            group_id += 1
        bag_to_group[i] = tuple_to_group[t]

DUP_MARKER_COLORS = [
    "#000000", "#e60000", "#0066cc", "#ff9900", "#00aa44",
    "#9933cc", "#cc0066", "#006666", "#996600", "#3366ff",
]

fig, ax = plt.subplots(figsize=(14, 24))
plt.subplots_adjust(top=0.93)

for i, (_, row) in enumerate(df_sorted.iterrows()):
    x_start = 0
    for color in color_order:
        count = row[color]
        if count > 0:
            ax.barh(i, count, left=x_start, height=1.0,
                    color=COLOR_HEX[color], edgecolor="none")
            x_start += count
    if is_duplicate[i]:
        gid = bag_to_group[i]
        marker_color = DUP_MARKER_COLORS[gid % len(DUP_MARKER_COLORS)]
        ax.plot(-1.0, i, "s", color=marker_color, markersize=6,
                markeredgecolor="white", markeredgewidth=0.3, zorder=5)

for i in range(1, n_bags):
    ax.axhline(y=i - 0.5, color="white", linewidth=0.3, zorder=4)

ax.set_yticks([])
max_skittles = int(df_sorted[color_order].sum(axis=1).max())
ax.set_xlim(-2.0, max_skittles + 0.5)
ax.set_xticks(range(0, max_skittles + 1, 5))
ax.set_ylim(-0.5, n_bags - 0.5)
ax.set_xlabel("Skittles per pack", fontsize=12)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)

fig.text(0.5, 0.965, "Colors in Full-Size Packs of Skittles",
         ha="center", va="center", fontsize=22, fontweight="bold")
fig.text(0.5, 0.943,
         f'{n_bags} packs (~60 Skittles each)  \u2014  only {n_dupes} are identical to another',
         ha="center", va="center", fontsize=14, fontstyle="italic", color="#333333")

ax.text(0.02, 0.02,
        f"\u25a0 = duplicate pack ({n_dupes} of {n_bags})\n"
        f"    matching packs share a colour",
        transform=ax.transAxes, fontsize=9, ha="left", va="bottom",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#cccccc"))

ax.text(max_skittles + 0.5, -n_bags * 0.03,
        "Data possibly-wrong  \u2022  Graph by @iamreddave",
        ha="right", va="top",
        fontsize=9, style="italic", color="gray", clip_on=False)

OUTPUT_FILE = f"skittles_possiblywrong_chart_{chart_version}.png"
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight", facecolor="white")
print(f"Chart saved to {OUTPUT_FILE}")
