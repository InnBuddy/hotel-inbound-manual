# -*- coding: utf-8 -*-
"""
ハラール市場データ可視化ダッシュボード
世界ハラール食品市場・日本ハラール食品市場・ハラールツーリズム市場の成長予測と需給ギャップ
"""

import plotly.graph_objects as go
import plotly.subplots as sp
import pandas as pd
import numpy as np

# ==========================================
# 1. データの生成（CAGRによる複利計算）
# ==========================================

# --- 世界ハラール食品市場（Straits Research）---
# 2025年: 2兆5,240億ドル → 2034年: 5兆7,406億ドル（CAGR 9.56%）
world_cagr = 9.56
world_2025 = 25240
world_2034 = 57406
years_world = list(range(2025, 2035))
world_values = [world_2025 * ((1 + world_cagr / 100) ** (y - 2025)) for y in years_world]

# --- 世界ハラール食品市場（GM Insights）：比較用 ---
# 2024年: 2.5兆ドル → 2034年: 6兆ドル（CAGR 9.1%）
gm_cagr = 9.1
gm_2024 = 25000
years_gm = list(range(2024, 2035))
gm_values = [gm_2024 * ((1 + gm_cagr / 100) ** (y - 2024)) for y in years_gm]

# --- 日本ハラール食品市場 ---
# 2025年: 1,735億ドル → 2034年: 3,474億ドル（CAGR 7.78%）
jp_cagr = 7.78
jp_2025 = 1735
jp_2034 = 3474
years_jp = list(range(2025, 2035))
jp_values = [jp_2025 * ((1 + jp_cagr / 100) ** (y - 2025)) for y in years_jp]

# --- ハラールツーリズム市場 ---
# 2021年: 2,152億6,000万ドル → 2028年: 3,104億5,000万ドル（CAGR 3.9%）
tourism_cagr = 3.9
tourism_2021 = 2152.6
tourism_2028 = 3104.5
years_tourism = list(range(2021, 2029))
tourism_values = [tourism_2021 * ((1 + tourism_cagr / 100) ** (y - 2021)) for y in years_tourism]

# ==========================================
# 2. ダッシュボードの作成
# ==========================================

fig = sp.make_subplots(
    rows=5, cols=1,
    subplot_titles=[
        "世界ハラール食品市場の成長予測（Straits Research）",
        "世界ハラール食品市場の成長予測（GM Insights 比較）",
        "日本ハラール食品市場の成長予測",
        "ハラールツーリズム市場の成長",
        "世界の需給ギャップ（需要 vs 供給）"
    ],
    vertical_spacing=0.08,
    specs=[
        [{"secondary_y": False}],
        [{"secondary_y": False}],
        [{"secondary_y": False}],
        [{"secondary_y": False}],
        [{"type": "pie"}],
    ]
)

# --- 色設定 ---
navy = "#1a2a3a"
royal = "#2a4a7f"
gold = "#D69E2E"
grey = "#718096"
green = "#2e7d32"

# ===== (a) 世界ハラール食品市場（Straits Research） =====
fig.add_trace(
    go.Bar(
        x=years_world,
        y=world_values,
        name="世界市場（Straits Research）",
        marker_color=navy,
        text=[f"{v:.0f}億ドル" for v in world_values],
        textposition="outside",
        textfont=dict(size=9, color=navy),
        hovertemplate="%{x}年: %{text}<extra></extra>"
    ),
    row=1, col=1
)
# トレンド線
fig.add_trace(
    go.Scatter(
        x=years_world,
        y=world_values,
        mode="lines+markers",
        name="トレンド",
        line=dict(color=gold, width=2, dash="dot"),
        marker=dict(size=6, color=gold),
        showlegend=False,
        hovertemplate="%{x}年: %{text}<extra></extra>",
        text=[f"{v:.0f}億ドル" for v in world_values]
    ),
    row=1, col=1
)

# ===== (b) GM Insights との比較 =====
fig.add_trace(
    go.Bar(
        x=years_gm,
        y=gm_values,
        name="世界市場（GM Insights）",
        marker_color=royal,
        text=[f"{v:.0f}億ドル" for v in gm_values],
        textposition="outside",
        textfont=dict(size=9, color=royal),
        hovertemplate="%{x}年: %{text}<extra></extra>"
    ),
    row=2, col=1
)
fig.add_trace(
    go.Scatter(
        x=years_world,
        y=world_values,
        mode="lines+markers",
        name="Straits Research（比較）",
        line=dict(color=gold, width=2, dash="dot"),
        marker=dict(size=6, color=gold),
        hovertemplate="Straits %{x}年: %{text}<extra></extra>",
        text=[f"{v:.0f}億ドル" for v in world_values]
    ),
    row=2, col=1
)

# ===== (c) 日本ハラール食品市場 =====
fig.add_trace(
    go.Bar(
        x=years_jp,
        y=jp_values,
        name="日本市場",
        marker_color=green,
        text=[f"{v:.0f}億ドル" for v in jp_values],
        textposition="outside",
        textfont=dict(size=9, color=green),
        hovertemplate="%{x}年: %{text}<extra></extra>"
    ),
    row=3, col=1
)

# ===== (d) ハラールツーリズム市場 =====
fig.add_trace(
    go.Bar(
        x=years_tourism,
        y=tourism_values,
        name="ツーリズム市場",
        marker_color=gold,
        text=[f"{v:.1f}億ドル" for v in tourism_values],
        textposition="outside",
        textfont=dict(size=9, color=gold),
        hovertemplate="%{x}年: %{text}<extra></extra>"
    ),
    row=4, col=1
)

# ===== (e) 需給ギャップ =====
fig.add_trace(
    go.Pie(
        labels=["需要（100%）", "供給不足（80%）"],
        values=[20, 80],
        marker=dict(colors=[green, "#E2E8F0"]),
        textinfo="label+percent",
        textfont=dict(size=12),
        hole=0.5,
        hovertemplate="%{label}<br>割合: %{percent}<extra></extra>"
    ),
    row=5, col=1
)

# ==========================================
# 3. レイアウト設定
# ==========================================

fig.update_layout(
    title=dict(
        text="<b>ハラール市場データ可視化ダッシュボード</b><br><span style='font-size:14px;color:#718096;'>世界・日本・ツーリズム市場の成長予測と需給分析</span>",
        font=dict(size=22, color=navy, family="Hiragino Sans, Meiryo, IPAGothic, sans-serif")
    ),
    height=1800,
    showlegend=True,
    template="plotly_white",
    font=dict(family="Hiragino Sans, Meiryo, IPAGothic, sans-serif", size=11, color="#2D3748"),
    hoverlabel=dict(
        font=dict(family="Hiragino Sans, Meiryo, IPAGothic, sans-serif", size=12)
    ),
    margin=dict(l=80, r=80, t=120, b=60),
)

# 各サブプロットの軸ラベル設定
# row 1
fig.update_xaxes(title_text="年度", row=1, col=1, tickfont=dict(size=10))
fig.update_yaxes(title_text="億ドル", row=1, col=1, tickfont=dict(size=10))
# row 2
fig.update_xaxes(title_text="年度", row=2, col=1, tickfont=dict(size=10))
fig.update_yaxes(title_text="億ドル", row=2, col=1, tickfont=dict(size=10))
# row 3
fig.update_xaxes(title_text="年度", row=3, col=1, tickfont=dict(size=10))
fig.update_yaxes(title_text="億ドル", row=3, col=1, tickfont=dict(size=10))
# row 4
fig.update_xaxes(title_text="年度", row=4, col=1, tickfont=dict(size=10))
fig.update_yaxes(title_text="億ドル", row=4, col=1, tickfont=dict(size=10))

# サブプロットタイトルの位置調整
for i in range(1, 6):
    fig.layout.annotations[i-1].update(font=dict(size=13, color=navy, family="Hiragino Sans, Meiryo, IPAGothic, sans-serif"))

# 需給ギャップの注釈
fig.add_annotation(
    text="<b>世界のハラール需要に対して<br>供給は約20%しか満たされていない</b>",
    xref="paper", yref="paper",
    x=0.5, y=0.12,
    showarrow=False,
    font=dict(size=13, color="#E53E3E", family="Hiragino Sans, Meiryo, IPAGothic, sans-serif"),
    bordercolor="#E53E3E",
    borderwidth=1,
    borderpad=8,
    bgcolor="rgba(255,255,255,0.9)",
    opacity=0.9
)

# ==========================================
# 4. 出力
# ==========================================

fig.write_html("halal_dashboard.html", auto_open=False)
fig.show()
