## v3.0.1
- 修正：恢復左側欄位功能（上傳/重新匯入 CSV、備份、回復上一次）
- UI 改為亮色系（新增 .streamlit/config.toml + 儀表板卡片樣式）

## v3.0.0
- 重構為商業儀表板風格
- 新增 KPI 指標卡片（品項數 / 平均毛利率 / 低毛利警示）
- 新增毛利率分布圖

## v2.1.0
- 新增關鍵字查詢：輸入關鍵字即可過濾顯示菜單資料
- 新增畫面欄位選擇：可選擇「菜單資料」畫面要顯示哪些欄位（不影響 DB）

## v2.0.9
- 新增「CSV 欄位輸出設定」：可控制匯出 CSV 要包含哪些欄位（不影響 DB）
- 可一鍵產生 data/menu_items_view.csv（依選擇欄位輸出）
- 新增「同步寫回 data/menu_items.csv（完整欄位）」按鈕

# 版本歷史

## v2.0.7
- 修正 pip 安裝時 wheel/packaging 相依警告：固定 wheel==0.45.1
- requirements 補上 wheel/pyarrow pin，減少環境差異

## v2.0.6
- 支援中文欄位 CSV 匯入：匯入時自動轉成英文欄位存入 DB
- Dashboard 以中文欄位顯示/編輯，儲存時轉回英文欄位
- 新增欄位：進貨重量（purchase_weight）、商品重量（unit_weight）


