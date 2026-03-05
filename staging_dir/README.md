

## 安裝失敗（出現 pyarrow / cmake）怎麼辦？
- 這版 run.sh 會先升級 pip 並偏好 wheel，通常可避免需要 cmake 的 source build。
- 若你之前的 venv 裡卡住了，建議刪掉 venv 後重跑：
  ```bash
  rm -rf venv
  ./run.sh
  ```

## 欄位設計（v2.0.6）
- **程式/資料庫內部統一用英文欄位**（穩定、好維護）。
- **CSV 可以是中文欄位或英文欄位**：匯入時會自動把中文欄位轉成英文存入 DB。
- Dashboard 顯示/編輯時會以 **中文欄位呈現**，但儲存時會轉回英文寫入 DB。

新增欄位：
- 進貨重量 → `purchase_weight`
- 商品重量 → `unit_weight`
