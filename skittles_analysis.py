"""
Skittles Analysis
-----------------
Loads raw Skittles bag data from the Excel spreadsheet,
cleans outliers, and produces a sorted stacked bar chart
with duplicate bags marked with a black dot.

Usage:
    pip install pandas openpyxl matplotlib
    python skittles_analysis.py
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter

# ── 1. LOAD ───────────────────────────────────────────────────────────────────

EXCEL_FILE = "skittles-megalist-3-6-25.xlsx"

df = pd.read_excel(EXCEL_FILE, sheet_name="Basic data")
df = df.drop(columns=["Unnamed: 0", "Matches?"])
df.columns = ["red", "orange", "yellow", "green", "purple"]
df = df.dropna(how="all").fillna(0).astype(int)

print(f"Loaded: {len(df)} bags")

# ── 2. CLEAN ──────────────────────────────────────────────────────────────────
# Keep only bags with 15–18 skittles (standard fun-size range).
# Outliers are consistent with data-entry errors, e.g. "26" instead of "2" + "6".

MIN_SKITTLES = 15
MAX_SKITTLES = 18

totals = df.sum(axis=1)
outliers = df[~totals.between(MIN_SKITTLES, MAX_SKITTLES)]
df = df[totals.between(MIN_SKITTLES, MAX_SKITTLES)].reset_index(drop=True)

print(f"Removed {len(outliers)} outlier bags (totals: {sorted(outliers.sum(axis=1).tolist())})")
print(f"Clean dataset: {len(df)} bags")

# ── 3. PREPARE ────────────────────────────────────────────────────────────────

COLORS = ["red", "orange", "yellow", "green", "purple"]

# COLOR_HEX = {
#     "red":    "#e60000",
#     "orange": "#ff9900",
#     "yellow": "#ffff00",
#     "green":  "#00ff00",
#     "purple": "#660066",
# }

COLOR_HEX = {
    "red":    "#c0043f",
    "orange": "#e64808",
    "yellow": "#f1be02",
    "green":  "#048207",
    "purple": "#441349",
}

# Order colours by total count across all bags (most common first)
color_order = df[COLORS].sum().sort_values(ascending=False).index.tolist()
print(f"Colour order (most→least): {color_order}")

# Sort bags: primary by count of most common colour, then next, etc.
sorted_indices = sorted(
    range(len(df)),
    key=lambda i: [df.loc[i, c] for c in color_order],
    reverse=True,
)
df_sorted = df.iloc[sorted_indices].reset_index(drop=True)

# Find duplicates
bag_tuples = [tuple(row) for row in df_sorted[color_order].values.tolist()]
counts = Counter(bag_tuples)
is_duplicate = [counts[t] > 1 for t in bag_tuples]
n_dupes = sum(is_duplicate)
n_unique = len(df_sorted) - n_dupes

# ── 4. PLOT (stacked horizontal bars, v3 style improved) ─────────────────────

n_bags = len(df_sorted)

# Assign a duplicate group ID so matching bags can be linked
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

fig, ax = plt.subplots(figsize=(14, 22))
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
        ax.plot(-0.5, i, "s", color=marker_color, markersize=3.5,
                markeredgecolor="white", markeredgewidth=0.3, zorder=5)

for i in range(1, n_bags):
    ax.axhline(y=i - 0.5, color="white", linewidth=0.3, zorder=4)

ax.set_yticks([])
max_skittles = int(df_sorted[color_order].sum(axis=1).max())
ax.set_xlim(-1.0, max_skittles + 0.5)
ax.set_xticks(range(0, max_skittles + 1))
ax.set_ylim(-0.5, n_bags - 0.5)
ax.set_xlabel("Skittles per bag", fontsize=12)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)

fig.text(0.5, 0.965, "Colors in Packets of Skittles",
         ha="center", va="center", fontsize=24, fontweight="bold")
fig.text(0.5, 0.943,
         f'"No two Rainbows are the same" \u2014 yet {n_dupes} of {n_bags} bags are identical to another',
         ha="center", va="center", fontsize=16, fontstyle="italic", color="#333333")

ax.text(0.02, 0.02,
        f"\u25a0 = duplicate bag ({n_dupes} of {n_bags})\n"
        f"    matching bags share a colour",
        transform=ax.transAxes, fontsize=9, ha="left", va="bottom",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#cccccc"))

ax.text(max_skittles + 0.5, -n_bags * 0.03,
        "Data Clare Wallace  \u2022  Graph by @iamreddave",
        ha="right", va="top",
        fontsize=9, style="italic", color="gray", clip_on=False)

OUTPUT_FILE = "skittles_chart_v9.png"
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight", facecolor="white")
print(f"Chart saved to {OUTPUT_FILE}")
