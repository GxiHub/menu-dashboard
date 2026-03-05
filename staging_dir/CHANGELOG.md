## v3.9.0_todo - 2026-02-22

### 多人待辦清單（Todo List）
- 新增 dashboard/pages/04_todo.py：多人協作待辦清單頁面（RBAC：require_editor）。
- 新增 app/todo_db.py：SQLite CRUD（todo_items、todo_tags、todo_item_tags、todo_activity_log）。
- 新增 bin/todo_reminder.py：定時提醒腳本（讀 remind_at，發 Telegram，idempotent via reminded_at）。
- 功能：建立任務（標題/描述/優先度/負責人/截止日/提醒時間/標籤）。
- 功能：快速切換狀態（open / doing / blocked / done）。
- 功能：篩選（關鍵字/狀態/範圍/標籤/隱藏完成）、排序（最近更新/截止日/優先度）。
- 功能：任務卡片內編輯、軟刪除（資料保留）、活動記錄。

## v3.8.0_rbac_edit_ux - 2026-02-22

### RBAC 權限控制（兩道門）
- 新增 dashboard/rbac.py：get_user_email()、require_editor()、require_admin()。
- email 來源：優先讀 Cf-Access-Authenticated-User-Email header，Streamlit WebSocket 環境下 fallback 讀 CF_Authorization cookie 解 JWT。
- 02_edit.py 加入 require_editor()，未授權者顯示 403。
- 新增 dashboard/pages/03_admin.py：Admin 專屬只讀頁（顯示版本號、現在時間、登入者 email）。
- Cloudflare Access App 設定：
  - dashboard.tfooddata.com/edit* 和 /admin* 需 Google 登入。
  - staging.tfooddata.com（整個網域）需 Google 登入。
  - Policy 允許：miniblackeye@gmail.com（Admin + Editor）、dejuice01@gmail.com（Editor）。

### Display 頁面
- 移除管理側邊欄（display 為公開頁面，不顯示部署/健康檢查按鈕）。
- 修正「清除」連結加 target="_self"，不再開新分頁。
- 商品詳細資訊：是否* 欄位值由 1/0 改顯示「是」/「否」。

### Edit 頁面全面簡化
- 移除 st.data_editor 表格模式及「儲存變更到 DB」、「重新計算毛利/毛利率」兩個按鈕。
- 改為「可搜尋商品列表」→ 點擊商品 → 單筆表單編輯（所有欄位分區顯示）。
- 儲存後直接寫入 DB，自動跳回 display 頁並展開剛編輯的商品。
- 返回按鈕回到編輯列表，保留搜尋關鍵字。

