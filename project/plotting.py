"""plotting.py — Visualisation helpers for topology/transpilation analysis."""

import math

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── Shared style constants ────────────────────────────────────────────────────
BG_DARK   = "#0D1117"
BG_PANEL  = "#161B22"
BORDER    = "#30363D"
TEXT_DIM  = "#8B949E"
TEXT_MAIN = "white"
OPT_LEVELS = [0, 1, 2, 3]


def _style_ax(ax, title="", ylabel=""):
    ax.set_facecolor(BG_PANEL)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)
    ax.tick_params(colors=TEXT_DIM, labelsize=9)
    if title:
        ax.set_title(title, color=TEXT_MAIN, fontsize=11, pad=8)
    if ylabel:
        ax.set_ylabel(ylabel, color=TEXT_DIM, fontsize=9)
    ax.grid(True, axis="y", color=BORDER, linewidth=0.6, linestyle="--")
    ax.set_axisbelow(True)


# ─────────────────────────────────────────────────────────────────────────────
# 1.  Logical circuit schematic
# ─────────────────────────────────────────────────────────────────────────────
def plot_logical_circuit(n_qubits: int, logical_circuit) -> plt.Figure:
    drawable_ops = [
        instr for instr in logical_circuit.data
        if instr.operation.name not in ("barrier", "measure")
    ]
    x_step = 0.5
    fig_w = max(13, min(22, 2.5 + len(drawable_ops) * x_step))
    fig, ax = plt.subplots(figsize=(fig_w, 3.5), facecolor=BG_DARK)
    ax.set_facecolor(BG_PANEL)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)
    ax.set_xlim(-0.5, max(10.5, 1.5 + len(drawable_ops) * x_step))
    ax.set_ylim(-0.8, n_qubits - 0.2)
    ax.set_title(
        f"Logical {logical_circuit.name} Circuit  (before transpilation)",
        color=TEXT_MAIN, fontsize=12, pad=8,
    )
    ax.axis("off")

    for q in range(n_qubits):
        y = n_qubits - 1 - q
        ax.axhline(y, color=BORDER, lw=1.2, xmin=0.02, xmax=0.98)
        ax.text(-0.35, y, f"q{q}", color=TEXT_DIM, va="center", ha="right", fontsize=10)

    gate_colors = {
        "h": "#2A9D8F",
        "u": "#2A9D8F",
        "p": "#2A9D8F",
        "cp": "#E63946",
        "cx": "#E63946",
        "cz": "#E63946",
        "swap": "#F4A261",
    }

    x = 0.6
    for instr in drawable_ops:
        op = instr.operation.name
        qubits = [logical_circuit.find_bit(q).index for q in instr.qubits]
        ys = [n_qubits - 1 - q for q in qubits]

        if len(qubits) == 1:
            color = gate_colors.get(op, "#457B9D")
            box = mpatches.FancyBboxPatch(
                (x - 0.22, ys[0] - 0.25), 0.44, 0.5,
                boxstyle="round,pad=0.04", facecolor=color,
                edgecolor="white", lw=1.0,
            )
            ax.add_patch(box)
            ax.text(x, ys[0], op.upper(), color="white", ha="center",
                    va="center", fontsize=8.5, fontweight="bold")
        elif op == "swap":
            ax.plot([x, x], [min(ys), max(ys)], color=TEXT_DIM, lw=1.2, zorder=3)
            for y in ys:
                ax.plot(x, y, "x", color=gate_colors["swap"], ms=10, mew=2, zorder=5)
        else:
            color = gate_colors.get(op, "#E63946")
            ax.plot([x, x], [min(ys), max(ys)], color=TEXT_DIM, lw=1.2, zorder=3)
            ax.plot(x, ys[0], "o", color=color, ms=8, zorder=5)
            ax.plot(x, ys[-1], "o", color="white", ms=13, zorder=4, mfc="none", mew=1.4)
            ax.text(x, ys[-1], op.upper(), color="white", ha="center",
                    va="center", fontsize=6.5, fontweight="bold", zorder=6)

        x += x_step

    for q in range(n_qubits):
        y = n_qubits - 1 - q
        mx = x + 0.25
        mb = mpatches.FancyBboxPatch(
            (mx - 0.22, y - 0.25), 0.44, 0.5,
            boxstyle="round,pad=0.05", facecolor="#264653", edgecolor=TEXT_DIM, lw=1,
        )
        ax.add_patch(mb)
        ax.text(mx, y, "M", color=TEXT_DIM, ha="center", va="center", fontsize=8)

    lops = logical_circuit.count_ops()
    ops_label = "  ".join(f"{k}: {v}" for k, v in lops.items() if k != "measure")
    ax.text(ax.get_xlim()[1] - 0.2, n_qubits - 0.8,
            f"depth: {logical_circuit.depth()}  |  {ops_label}",
            color="#2A9D8F", fontsize=10, ha="right")

    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 2.  Topology diagrams (all three side-by-side)
# ─────────────────────────────────────────────────────────────────────────────
def plot_topologies(topologies: dict) -> plt.Figure:
    n = len(topologies)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4.5), facecolor=BG_DARK)
    fig.suptitle("Physical Qubit Topologies", color=TEXT_MAIN, fontsize=14, y=1.01)

    for ax, (tname, topo) in zip(axes, topologies.items()):
        cmap  = topo["map"]
        color = topo["color"]
        short = topo["short"]
        desc  = topo["description"]
        ibm   = topo["ibm_device"]

        ax.set_facecolor(BG_PANEL)
        for sp in ax.spines.values():
            sp.set_edgecolor(BORDER)
        ax.set_title(short, color=TEXT_MAIN, fontsize=12, pad=8)
        ax.axis("off")

        nq = cmap.size()
        angles = [2 * math.pi * i / nq - math.pi / 2 for i in range(nq)]
        xs = [math.cos(a) for a in angles]
        ys = [math.sin(a) for a in angles]

        drawn = set()
        for u, v in cmap.get_edges():
            if (v, u) not in drawn:
                ax.plot([xs[u % nq], xs[v % nq]], [ys[u % nq], ys[v % nq]],
                        color=BORDER, lw=1.8, zorder=1)
                drawn.add((u, v))

        ax.scatter(xs, ys, s=320, color=color, zorder=3,
                   edgecolors="white", linewidths=1.3)
        for i, (x, y) in enumerate(zip(xs, ys)):
            ax.text(x, y, str(i), ha="center", va="center",
                    color="white", fontsize=8, fontweight="bold", zorder=4)

        edge_count = len(list(cmap.get_edges())) // 2
        ax.text(0, -1.45,
                f"{desc}\n\nEdges: {edge_count}  |  Qubits: {nq}\n"
                f"Example device: {ibm}",
                ha="center", va="top", color=TEXT_DIM,
                fontsize=8.5, multialignment="center")

        ax.set_xlim(-1.7, 1.7)
        ax.set_ylim(-1.9, 1.5)

    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 3.  Bar charts: Opt-0 vs Opt-3 side-by-side  ← FIXED
# ─────────────────────────────────────────────────────────────────────────────
def plot_opt3_bars(topologies: dict, results: dict) -> plt.Figure:
    """
    Show Opt-0 (naive) and Opt-3 (best) side-by-side for each metric so the
    optimiser's impact is immediately visible.  Previously only Opt-3 was shown,
    making all topologies look identical.
    """
    topo_keys   = list(topologies.keys())
    colors_list = [topologies[t]["color"] for t in topo_keys]
    shorts      = [topologies[t]["short"] for t in topo_keys]
    n           = len(topo_keys)
    x_pos       = np.arange(n)
    bar_w       = 0.35          # two bars per topology, with a gap

    metrics = [
        ("depth",       "Gate layers",  "Circuit Depth"),
        ("cx",          "CX gates",     "CX Gate Count"),
        ("swap_est",    "≈ SWAPs",       "SWAP Overhead"),
        ("total_gates", "Total gates",  "Total Gate Count"),
    ]

    fig, axes = plt.subplots(1, 4, figsize=(20, 5), facecolor=BG_DARK)
    fig.suptitle(
        "Compiled Cost — Opt-0  (naive)  vs  Opt-3  (best)",
        color=TEXT_MAIN, fontsize=13, y=1.03,
    )

    ALPHA_DIM = 0.45   # Opt-0 bars rendered lighter

    for ax, (key, ylabel, title) in zip(axes, metrics):
        vals0 = [results[t][0][key] for t in topo_keys]
        vals3 = [results[t][3][key] for t in topo_keys]
        y_max = max(max(vals0), max(vals3), 1)

        # Opt-0 bars — left, desaturated
        bars0 = ax.bar(x_pos - bar_w / 2, vals0, bar_w,
                       color=colors_list, alpha=ALPHA_DIM,
                       edgecolor="none", zorder=3, label="Opt-0")
        # Opt-3 bars — right, full colour
        bars3 = ax.bar(x_pos + bar_w / 2, vals3, bar_w,
                       color=colors_list, alpha=1.0,
                       edgecolor="white", linewidth=0.6,
                       zorder=3, label="Opt-3")

        for bar, v in zip(bars0, vals0):
            if v > 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        v + y_max * 0.02, str(v),
                        ha="center", va="bottom",
                        color=TEXT_DIM, fontsize=9)

        for bar, v in zip(bars3, vals3):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    v + y_max * 0.02, str(v),
                    ha="center", va="bottom",
                    color="white", fontsize=9, fontweight="bold")

        ax.set_xticks(x_pos)
        ax.set_xticklabels(shorts, color=TEXT_DIM, fontsize=9)
        ax.set_ylim(0, y_max * 1.28)
        _style_ax(ax, title, ylabel)

    # Shared legend — Opt-0 / Opt-3 indicator patches
    legend_patches = [
        mpatches.Patch(color="grey", alpha=ALPHA_DIM, label="Opt-0  (naive)"),
        mpatches.Patch(color="grey", alpha=1.0,       label="Opt-3  (best)"),
    ]
    fig.legend(handles=legend_patches, loc="upper right", ncol=2,
               facecolor=BG_PANEL, edgecolor=BORDER,
               labelcolor=TEXT_MAIN, fontsize=10,
               bbox_to_anchor=(0.99, 1.06))

    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 4.  Line chart: depth vs optimisation level
# ─────────────────────────────────────────────────────────────────────────────
def plot_depth_vs_opt(topologies: dict, results: dict) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 4.5), facecolor=BG_DARK)
    _style_ax(ax, "Circuit Depth  vs  Optimisation Level", "Depth (gate layers)")

    for tname, topo in topologies.items():
        depths = [results[tname][o]["depth"] for o in OPT_LEVELS]
        ax.plot(OPT_LEVELS, depths, "o-",
                color=topo["color"], label=topo["short"], lw=2.5, ms=8)
        for o, d in zip(OPT_LEVELS, depths):
            ax.text(o, d + 0.5, str(d), ha="center",
                    color=topo["color"], fontsize=9.5, fontweight="bold")

    ax.set_xticks(OPT_LEVELS)
    ax.set_xticklabels([f"Level {o}" for o in OPT_LEVELS], color=TEXT_DIM)
    ax.legend(facecolor=BG_PANEL, edgecolor=BORDER, labelcolor=TEXT_MAIN, fontsize=10)
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 5.  Grouped bar: CX count at every opt level
# ─────────────────────────────────────────────────────────────────────────────
def plot_cx_by_opt(topologies: dict, results: dict) -> plt.Figure:
    topo_keys = list(topologies.keys())
    n_topos   = len(topo_keys)
    bar_w     = 0.22
    x_base    = np.arange(len(OPT_LEVELS))

    fig, ax = plt.subplots(figsize=(10, 4.5), facecolor=BG_DARK)
    _style_ax(ax, "CX Gate Count  across all Optimisation Levels", "CX gates")

    for i, tname in enumerate(topo_keys):
        cx_vals = [results[tname][o]["cx"] for o in OPT_LEVELS]
        offset  = (i - n_topos / 2 + 0.5) * bar_w
        bars    = ax.bar(x_base + offset, cx_vals, bar_w,
                         color=topologies[tname]["color"],
                         label=topologies[tname]["short"],
                         edgecolor="none", zorder=3)
        for bar, v in zip(bars, cx_vals):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    v + 0.4, str(v),
                    ha="center", va="bottom",
                    color=topologies[tname]["color"], fontsize=8)

    ax.set_xticks(x_base)
    ax.set_xticklabels([f"Opt-{o}" for o in OPT_LEVELS], color=TEXT_DIM)
    ax.legend(facecolor=BG_PANEL, edgecolor=BORDER, labelcolor=TEXT_MAIN, fontsize=10)
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 6.  Summary heatmap — all optimisation levels
# ─────────────────────────────────────────────────────────────────────────────
def plot_heatmap(topologies: dict, results: dict) -> plt.Figure:
    """
    Rows  = topology × opt-level combinations (e.g. Linear/Opt-0, Linear/Opt-3 …)
    Cols  = metrics
    Previously only Opt-3 was shown, making every row identical and the colour
    encoding meaningless.  Now all opt levels are included so real variation
    shows up in the colours.
    """
    topo_keys = list(topologies.keys())
    metrics   = ["depth", "cx", "u", "swap_est", "total_gates"]
    mlabels   = ["Depth", "CX", "U gates", "≈SWAPs", "Total gates"]

    # Build rows: one per (topology, opt_level) pair.
    show_opts = [0, 1, 2, 3]
    row_labels = []
    data_rows  = []

    for tname in topo_keys:
        short = topologies[tname]["short"]
        for opt in show_opts:
            row_labels.append(f"{short} / O{opt}")
            data_rows.append([results[tname][opt][m] for m in metrics])

    data = np.array(data_rows, dtype=float)

    # Column-wise normalisation so each metric is independently colour-scaled
    col_max = data.max(axis=0)
    col_max[col_max == 0] = 1
    norm_data = data / col_max

    n_rows = len(row_labels)
    fig_h  = max(4.5, n_rows * 0.55 + 1.5)
    fig, ax = plt.subplots(figsize=(10, fig_h), facecolor=BG_DARK)
    ax.set_facecolor(BG_PANEL)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)
    ax.set_title(
        "Metric Heatmap  (all opt levels, column-normalised)\n"
        "Green = cheapest · Red = most expensive",
        color=TEXT_MAIN, fontsize=12, pad=10,
    )

    im = ax.imshow(norm_data, aspect="auto", cmap="RdYlGn_r", vmin=0, vmax=1)

    ax.set_xticks(range(len(mlabels)))
    ax.set_xticklabels(mlabels, color=TEXT_DIM, fontsize=10)
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels(row_labels, color=TEXT_MAIN, fontsize=9)

    # Horizontal dividers between topology groups
    for g in range(1, len(topo_keys)):
        ax.axhline(g * len(show_opts) - 0.5, color=BORDER, lw=1.5)

    for i in range(n_rows):
        for j in range(len(metrics)):
            raw = int(data[i, j])
            ax.text(j, i, str(raw), ha="center", va="center",
                    color="white", fontsize=10, fontweight="bold")

    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cb.ax.tick_params(colors=TEXT_DIM, labelsize=8)
    cb.set_label("Relative cost  (0 = best, 1 = worst)", color=TEXT_DIM, fontsize=8)

    fig.tight_layout()
    return fig
