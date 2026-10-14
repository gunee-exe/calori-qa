"""Static charts for the report (light surface; printed document, so no hover layer).

Palette from the dataviz reference instance: status good/critical for pass/fail
(always paired with a text label), series-1 blue for single-series bars, and the
blue ordinal ramp (steps 250 -> 650) for ordered categories such as severity.
"""
import json
import pathlib
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import design_requirements as R
import design_testcases as T
import defects as D

HERE = pathlib.Path(__file__).parent
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)

SURFACE = "#fcfcfb"; INK = "#0b0b0b"; INK2 = "#52514e"; MUTED = "#898781"; GRID = "#e1e0d9"; AXIS = "#c3c2b7"
GOOD = "#0ca30c"; CRIT = "#d03b3b"; BLUE = "#2a78d6"
ORDINAL = {"Trivial": "#86b6ef", "Minor": "#3987e5", "Major": "#256abf", "Critical": "#104281",
           "Low": "#86b6ef", "Medium": "#3987e5", "High": "#104281"}

plt.rcParams.update({"font.family": ["Calibri", "Carlito"], "font.size": 11, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
                     "savefig.facecolor": SURFACE})

results = json.loads((HERE / "results.json").read_text(encoding="utf-8"))


def style(ax, xgrid=True):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    if xgrid:
        ax.xaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
    ax.tick_params(length=0)


def pass_fail_donut():
    c = Counter(r["status"] for r in results.values())
    vals = [c.get("Pass", 0), c.get("Fail", 0)]
    fig, ax = plt.subplots(figsize=(5.2, 3.6), dpi=200)
    wedges, _ = ax.pie(vals, colors=[GOOD, CRIT], startangle=90, counterclock=False,
                       wedgeprops=dict(width=0.38, edgecolor=SURFACE, linewidth=2))
    total = sum(vals)
    ax.text(0, 0.08, f"{total}", ha="center", va="center", fontsize=26, color=INK, fontweight="bold")
    ax.text(0, -0.2, "test cases executed", ha="center", va="center", fontsize=10, color=INK2)
    labels = [f"Passed  {vals[0]}  ({vals[0] / total:.1%})", f"Failed  {vals[1]}  ({vals[1] / total:.1%})"]
    ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1.0, 0.5), frameon=False, fontsize=11,
              labelcolor=INK, handlelength=1.2)
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(OUT / "pass_fail.png", bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def module_results():
    mods = list(R.MODULES)
    p = [sum(1 for t in T.TEST_CASES if t["module"] == m and results[t["id"]]["status"] == "Pass") for m in mods]
    f = [sum(1 for t in T.TEST_CASES if t["module"] == m and results[t["id"]]["status"] == "Fail") for m in mods]
    labels = [f"{m}  {R.MODULES[m]}" for m in mods]
    fig, ax = plt.subplots(figsize=(7.6, 3.9), dpi=200)
    y = range(len(mods))[::-1]
    ax.barh(list(y), p, color=GOOD, height=0.62, label="Passed", edgecolor=SURFACE, linewidth=2)
    ax.barh(list(y), f, left=p, color=CRIT, height=0.62, label="Failed", edgecolor=SURFACE, linewidth=2)
    for yi, pi, fi in zip(y, p, f):
        if pi:
            ax.text(pi / 2, yi, str(pi), ha="center", va="center", color="white", fontsize=10, fontweight="bold")
        if fi:
            ax.text(pi + fi / 2, yi, str(fi), ha="center", va="center", color="white", fontsize=10, fontweight="bold")
    ax.set_yticks(list(y)); ax.set_yticklabels(labels, fontsize=10, color=INK)
    ax.set_xlabel("Test cases")
    style(ax)
    ax.legend(loc="lower center", bbox_to_anchor=(0.45, 1.0), ncol=2, frameon=False, fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "module_results.png")
    plt.close(fig)


def defects_by_module():
    c = Counter(dx["module"] for dx in D.DEFECTS)
    mods = sorted(R.MODULES, key=lambda m: (c.get(m, 0), m))
    fig, ax = plt.subplots(figsize=(7.6, 3.6), dpi=200)
    vals = [c.get(m, 0) for m in mods]
    ax.barh([f"{m}  {R.MODULES[m]}" for m in mods], vals, color=BLUE, height=0.62)
    for i, v in enumerate(vals):
        ax.text(v + 0.15, i, str(v), va="center", color=INK, fontsize=10)
    ax.set_xlabel("Defects")
    ax.tick_params(axis="y", labelsize=10, labelcolor=INK)
    style(ax)
    fig.tight_layout()
    fig.savefig(OUT / "defects_by_module.png")
    plt.close(fig)


def severity_priority():
    sev_order = ["Critical", "Major", "Minor", "Trivial"]
    pri_order = ["High", "Medium", "Low"]
    cs = Counter(dx["severity"] for dx in D.DEFECTS)
    cp = Counter(dx["priority"] for dx in D.DEFECTS)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 3.0), dpi=200)
    for ax, order, c, title in ((a1, sev_order, cs, "By severity"), (a2, pri_order, cp, "By priority")):
        vals = [c.get(k, 0) for k in order]
        bars = ax.bar(order, vals, color=[ORDINAL[k] for k in order], width=0.6)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.3, str(v), ha="center", color=INK, fontsize=10)
        ax.set_title(title, color=INK, fontsize=11, loc="left")
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.yaxis.grid(True, color=GRID, linewidth=0.8); ax.set_axisbelow(True); ax.tick_params(length=0)
        ax.set_ylim(0, max(vals) + 3)
    a1.set_ylabel("Defects")
    fig.tight_layout()
    fig.savefig(OUT / "severity_priority.png")
    plt.close(fig)


if __name__ == "__main__":
    pass_fail_donut(); module_results(); defects_by_module(); severity_priority()
    print(sorted(p.name for p in OUT.glob("*.png")))
