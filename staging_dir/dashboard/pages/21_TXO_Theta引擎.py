from rbac import require_page, log_access
import streamlit as st

_PAGE = "TXO Theta引擎"
email = require_page(_PAGE)
log_access(email, _PAGE)

st.title("TXO Theta Engine")
st.caption("系統設計 · 策略邏輯 · 風控規則 · 開發路線圖")

tab1, tab2, tab3, tab4 = st.tabs(["策略邏輯", "風控規則", "工具比較", "開發路線"])

# ─────────────────────────────────────────────────────────────
with tab1:
    st.subheader("核心思想")
    st.markdown("""
美股 **ThetaGang** 策略的核心是系統化賣出被高估的波動率，靠時間價值衰退（Theta）獲利。
台灣目前沒有人將此概念完整移植到 TXO 台指選擇權市場。

**兩種主力策略依 IV Rank 切換：**
""")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
**⚡ Short Strangle（主力）**
- 進場條件：IV Rank > 50%
- 同時賣出 OTM Call + OTM Put
- Delta 目標：各 ±0.15
- 停利：收取權利金的 **50%**
- 停損：虧損達權利金的 **200%**
- 最大風險：理論無限（嚴格停損）
- 優點：Theta 收入最大化
""")
    with col2:
        st.markdown("""
**🛡 Iron Condor（保守）**
- 進場條件：IV Rank 30–50%
- Short Strangle + 外側保護翼
- Delta 目標：各 ±0.15，翼 ±0.05
- 停利：收取權利金的 **50%**
- 停損：虧損達最大風險的 **100%**
- 最大風險：**有限**（已知上限）
- 優點：黑天鵝保護
""")

    st.divider()
    st.subheader("每日盤後決策流程（15:05 自動執行）")
    st.code("""
▶ 每日 15:05 觸發
  ├─ 計算 TXO ATM IV & IV Rank（過去252日）
  ├─ 計算組合總 Delta 偏移量
  ├─ 確認距到期日 DTE
  ├─ 掃描近期事件（Fed / 台股特殊結算）
  └─ 決策：
       IF IV Rank > 50% AND DTE >= 21 AND 無重大事件
           → 建議 Short Strangle（自動計算最佳履約價）
       IF IV Rank 30–50% AND DTE >= 21
           → 建議 Iron Condor
       IF IV Rank < 30% OR DTE < 7
           → 不進場，等待更好時機
       持倉監控：50% 獲利停利 / 200% 虧損停損 → 自動平倉
""", language="")

    st.divider()
    st.subheader("系統五層架構")
    layers = [
        ("1 資料層", "Shioaji 即時報價、FinMind 歷史庫、Black-Scholes IV 反推、SQLite"),
        ("2 訊號層", "IV Rank 模組、Delta 中性評估、事件日曆，第二期加入 GARCH 波動率預測"),
        ("3 風控層", "單筆最大虧損 2% 資金、組合 Delta ±50 閾值、DTE<7 強制平倉、大盤跌 3% 暫停"),
        ("4 執行層", "永豐金 Shioaji Python API、TXO 期選下單、ROD 限價單、自動平倉觸發"),
        ("5 監控層", "Pi53 Streamlit 看板（此系統）、Telegram Bot 每日報告、Greeks 即時顯示"),
    ]
    for name, desc in layers:
        with st.expander(name, expanded=True):
            st.write(desc)

# ─────────────────────────────────────────────────────────────
with tab2:
    st.subheader("8 條硬性風控規則")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**進場規則**")
        rules_in = [
            ("01", "IV Rank 門檻", "Strangle 需 >50%；Condor 需 30–50%；否則不進場"),
            ("02", "DTE 控制", "距到期至少 21 天才開新倉，避免 Gamma 風險暴增"),
            ("03", "部位上限", "最多 2 個 Strangle 或 3 個 Condor，避免過度集中"),
            ("04", "事件迴避", "Fed 決策日、台股特殊結算前 3 天不開新倉"),
        ]
        for num, title, desc in rules_in:
            st.markdown(f"**{num} {title}**\n\n{desc}")
            st.divider()
    with col_b:
        st.markdown("**停損停利規則**")
        rules_out = [
            ("05", "停利", "單筆獲利達收入權利金 50% → 自動平倉，不貪"),
            ("06", "停損", "單筆虧損達收入權利金 200% → 強制平倉"),
            ("07", "Delta 中性", "組合 Delta 超過 ±50 → 買期貨中和方向性風險"),
            ("08", "黑天鵝", "台指單日跌超 3% → 系統暫停，等人工確認再進場"),
        ]
        for num, title, desc in rules_out:
            st.markdown(f"**{num} {title}**\n\n{desc}")
            st.divider()

# ─────────────────────────────────────────────────────────────
with tab3:
    st.subheader("台股 API 工具比較")
    import pandas as pd
    df_api = pd.DataFrame([
        {"券商": "永豐金 Shioaji", "選擇權下單": "✅ TXO完整", "期貨": "✅", "Python": "✅ 原生", "文件": "★★★★★", "推薦": "⭐ 首選"},
        {"券商": "元富 MasterLink", "選擇權下單": "✅", "期貨": "✅", "Python": "✅ Python+C#", "文件": "★★★★", "推薦": "次選"},
        {"券商": "富邦 Fubon Neo", "選擇權下單": "⚠️ 期貨有", "期貨": "✅", "Python": "✅", "文件": "★★★", "推薦": "可用"},
        {"券商": "富果 Fugle", "選擇權下單": "❌ 不支援", "期貨": "❌", "Python": "✅", "文件": "★★★★", "推薦": "不適用"},
        {"券商": "元大證券", "選擇權下單": "⚠️ 文件少", "期貨": "⚠️", "Python": "⚠️ 有限", "文件": "★★", "推薦": "不建議"},
    ])
    st.dataframe(df_api, width="stretch", hide_index=True)

    st.divider()
    st.subheader("美股策略移植台股可行性")
    df_compare = pd.DataFrame([
        {"策略": "Wheel（個股）", "美股": "流動性極高，成熟", "台指TXO": "個股選擇權幾乎無流動性", "移植": "❌ 不可行"},
        {"策略": "Short Strangle（指數）", "美股": "SPX每日到期，競爭激烈", "台指TXO": "TXO月選，近月流動尚可", "移植": "✅ 最適合"},
        {"策略": "Iron Condor（指數）", "美股": "成熟，大量競爭", "台指TXO": "TXO可行，競爭者極少", "移植": "✅ 可行"},
        {"策略": "Delta-Neutral Rebalance", "美股": "成本低，可高頻", "台指TXO": "手續費高，需仔細計算", "移植": "⚠️ 謹慎"},
        {"策略": "IV預測 + 賣方", "美股": "VIX研究豐富", "台指TXO": "TXO IV研究幾乎空白", "移植": "✅ 最大護城河"},
        {"策略": "自動化API執行", "美股": "IBKR/Alpaca極成熟", "台指TXO": "Shioaji可用，文件齊全", "移植": "✅ 技術可行"},
    ])
    st.dataframe(df_compare, width="stretch", hide_index=True)

# ─────────────────────────────────────────────────────────────
with tab4:
    st.subheader("六階段開發路線圖")
    roadmap = [
        ("Week 1–2", "地基", "永豐金帳戶 + Shioaji 串接",
         ["開立永豐金帳戶，申請期貨選擇權交易資格",
          "申請 Shioaji API Token，完成 Python 環境",
          "成功拉取 TXO 即時報價（Bid/Ask/Delta）",
          "寫入 SQLite，確認資料格式"]),
        ("Week 3–4", "核心模組", "IV 計算引擎 + 歷史資料庫",
         ["Black-Scholes 反推每個履約價的 IV",
          "建立 IV Rank（過去 252 交易日）",
          "從 FinMind 補充歷史 TXO 日資料（2020 起）",
          "每日盤後自動入庫"]),
        ("Week 5–6", "策略+風控", "進出場邏輯 + Paper Trading",
         ["IV Rank 進場條件判斷",
          "履約價自動選擇（目標 Delta 0.15）",
          "停利 50% / 停損 200% 觸發機制",
          "Paper Trading 模擬 2 個月"]),
        ("Week 7–8", "監控", "Dashboard + Telegram 上線",
         ["Pi53 Streamlit 看板（即時 Greeks、損益、IV Rank）",
          "Telegram Bot：每日盤後報告 + 觸發即時警報",
          "Delta 偏移超閾值自動通知"]),
        ("Month 3", "實盤", "小額真實資金測試（1 口）",
         ["Shioaji 真實下單 1 口 TXO Strangle",
          "驗證滑價、手續費、流動性假設",
          "修正系統與市場實際的差異"]),
        ("Month 4–6", "進化", "IV 預測模型（護城河）",
         ["GARCH 模型預測未來 5 日 Realized Volatility",
          "IV vs RV 差 = Volatility Risk Premium → 進場強度依據",
          "LSTM 嘗試：用 IV 期限結構預測方向",
          "逐步擴大部位規模"]),
    ]
    for period, phase, title, tasks in roadmap:
        with st.expander(f"**{period}** · {phase} — {title}"):
            for t in tasks:
                st.markdown(f"- {t}")
