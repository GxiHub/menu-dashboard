# Pi Fleet Audit Bot

**類型：** 自動化維運　｜　**版本：** v1.0　｜　**建立：** 2026-04-21

> 每天自動掃描所有節點，用 AI 分析狀態，Telegram 通知行動清單

---

## 系統架構

```
每天 09:00（cron）
      ↓
audit.sh（pi53 上執行）
      ├── SSH 掃 pi52、pi54、pi51
      │   ├── 執行中服務（與上次比對 → 偵測新增）
      │   ├── git 狀態（uncommitted / unpushed）
      │   ├── 不在 git 的新腳本/程式
      │   ├── 開放 port 清單
      │   └── 磁碟使用率
      │
      ├── 產生 raw_report.md
      │
      └── claude -p（AI 分析）
            ↓
      結構化行動清單
            ↓
      Telegram 通知 + 儲存報告
```

---

## 輸出格式

```
🔴 需要立刻處理
• [pi54] 磁碟 89% → 清理或換大 SD 卡
• [pi52] proxy.py 未 commit → git push

🟡 建議處理
• [pi54] pi54-app 無文件 → 補 README
• [pi52] 無 crontab 備份 → 加 github_backup

🟢 狀態良好
• fleet/ → raspi-system ✅
• pi53 所有服務正常

📊 整體評分：X/10
```

---

## 檔案位置

| 項目 | 路徑 |
|------|------|
| 主腳本 | `~/audit.sh` |
| GitHub 備份 | `GxiHub/raspi-system/audit.sh` |
| 報告輸出 | `~/logs/audit/report_YYYY-MM-DD.md` |
| 節點 snapshot | `~/logs/audit/snapshots/<node>_services.txt` |
| Cron | 每天 09:00 |

---

## 觸發方式

```bash
# 手動執行（隨時可跑）
bash ~/audit.sh

# 看最新報告
cat ~/logs/audit/$(ls ~/logs/audit/ | grep report | tail -1)

# 看 cron log
tail -f ~/logs/audit/cron.log
```

---

## AI 分類規則

| 分類 | 觸發條件 |
|------|---------|
| 🔴 立刻處理 | 磁碟 >85%、重要檔案未 git、服務異常 |
| 🟡 建議處理 | 新服務無文件、腳本未備份、port 無 auth |
| 🟢 狀態良好 | 備份正常、服務健康、磁碟充裕 |

---

## 擴充方向

- 加入 pi51（上線後）
- 偵測 port 有無 auth（嘗試無 token 存取）
- 自動 PR：把未備份的腳本自動 commit 到 GitHub
- 週報：每週日彙整一週的 audit 結果
