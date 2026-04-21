# UberEats 印表機 Proxy 測試紀錄

**類型：** 測試驗收　｜　**日期：** 2026-04-21　｜　**狀態：** ✅ 全部通過

---

## 架構

```
UberEats 平板1 (192.168.1.119) ─┐
UberEats 平板2 (192.168.1.115) ─┤→ pi52 proxy TM-m30II (192.168.1.109) → 印表機 TM-m30III (192.168.1.124)
POS (tong.tfooddata.com)        ─┘
```

---

## 驗收結果

| 來源 | 結果 |
|------|------|
| UberEats 平板 1（192.168.1.119） | ✅ 正常出單 |
| UberEats 平板 2（192.168.1.115） | ✅ 正常出單 |
| POS 列印按鈕 | ✅ 正常出單 |

---

## 根本問題與修復

### 問題：平板無法找到印表機
- **根因：** `proxy.py` 的 `MY_IP = "192.168.0.21"`（舊網段），平板收到探索回應後連不上
- **修復：** 改為 `MY_IP = "192.168.1.109"`，`PRINTER_IP = "192.168.1.124"`

### 問題：兩台平板都顯示「無法連線」
- **根因：** Epson 只允許一條 TCP，一台在用另一台就顯示錯誤
- **結論：** 設定頁顯示「無法連線」是正常的，**實際有訂單時自動連線印出**

### 問題：pi54 也裝了 printer-proxy
- **根因：** 今天部署 fleet 時 pi54 也被部署了 proxy，搶佔了印表機連線
- **修復：** pi54 的 printer-proxy 保持停止狀態

---

## 兩台平板運作機制

- 兩台都連到 **TM-m30II（pi52 假裝的）**，不是真實的 TM-m30III
- 一次只有一台「持有」連線（WHO_IS_HOLDING 協議）
- 實際印單時每次約 1-2 秒，印完自動釋放，另一台接著用
- **不會同時搶印，但也不會互相卡死**

---

## 重要設定

| 項目 | 值 |
|------|-----|
| proxy IP | 192.168.1.109 |
| proxy MAC | 2c:cf:67:6b:0c:89 |
| 假裝型號 | TM-m30II |
| 真實印表機 | 192.168.1.124:9100 |
| POS 注入 port | 9200（localhost） |
| 穩定備份 | `/home/pi52/proxy.py.stable.20260421` |

---

## 排查 SOP

1. `sudo systemctl status printer-proxy`（在 pi52）
2. `tail -20 /home/pi52/proxy.log`
3. 確認 MY_IP=192.168.1.109、PRINTER_IP=192.168.1.124
4. 確認 pi54 的 proxy 是停止的
5. 平板重新掃描 → 選 TM-m30II（不是 TM-m30III）

---

## 印表機版面設定（2026-04-21）

### 問題
- UberEats 訂單的**已付金額**和**客人姓名右側**被切掉
- 原因：TM-m30III 印表機的可印區域設定不正確

### 修復步驟
1. 停止 proxy（讓手機可以直接連印表機）：
2. 用 **Epson TM Utility** 連線到 192.168.1.124
3. 進入 **Memory Switches** → **Print Area Width**
4. 設定為 **80mm × 48mm**（紙寬 80mm，可印高 48mm）
5. 存入印表機 → 重新開機
6. 重啟 proxy：

### 結果
✅ 版面恢復正常，金額和訂單號完整顯示

---

## UberEats 訂單自動整合（2026-04-21）

### 架構

```
UberEats 平板出單 → pi52 proxy 攔截 ESC/POS → 儲存 PNG
                                                    ↓
pi53 ubereats-sync 服務（每 5 秒）
→ SSH 到 pi52 跑 OCR（Tesseract + chi_tra）
→ 解析訂單號、品項、金額
→ 自動建立到 luwei-manager 訂單列表
```

### 關鍵檔案

| 檔案 | 位置 | 說明 |
|------|------|------|
| ocr_helper.py | pi52:/home/pi52/ | OCR 解析 + 輸出 JSON |
| ubereats_auto.py | pi53:/home/pi53/ | 主監控腳本 |
| ubereats-sync.service | pi53 systemd | 開機自動啟動 |

### OCR 技術細節

- Tesseract 裝在 **pi52**（pi53 安裝失敗）
- pi53 透過 SSH 呼叫 pi52 的 ocr_helper.py
- Header 區域（白字黑底）需反轉後再 OCR 才能讀取訂單號
- 訂單號格式：4-8 個英數字（含 2+ 大寫字母），如 8EE80、A48BE
- 已知品項對照表：18 種 UberEats 英文品名 → luwei-manager product_id

### 已驗證

✅ 訂單號（如 8EE80）自動帶入  
✅ 金額正確（已付金額）  
✅ 品項自動對應 luwei-manager 商品  
✅ 訂單出現在 pos/orders 列表  
⚠️ 客人名 OCR 不穩定（深色背景白字難辨）

---

## Reboot 後持續運作確認（2026-04-21）

### 設定完成

| 項目 | 狀態 |
|------|------|
| pi52 `printer-proxy.service` | ✅ enabled，reboot 後自動啟動 |
| pi52 IP | ✅ 改為**靜態 192.168.1.109**（防止 DHCP 變動） |
| pi54 `printer-proxy.service` | ✅ disabled（不再搶佔印表機） |

### UberEats 自動整合待辦

- 目前狀況：訂單號 ✅、金額 ✅、有英文名的品項 ✅、純中文品項 OCR 不準確
- 改善方向：放大圖片 3x OCR + 保留 PRODUCT_MAP 對英文品名
- 目標：進 KDS + 訂單紀錄（待處理）

### Reboot 實測結果（2026-04-21 13:38）

✅ pi52 重開機後：
- IP 維持 192.168.1.109（靜態設定生效）
- printer-proxy 自動啟動（13:38:24 BST）
- 印表機 5 秒內自動重連（13:38:36）
- **列印功能完全恢復，無需手動操作**
