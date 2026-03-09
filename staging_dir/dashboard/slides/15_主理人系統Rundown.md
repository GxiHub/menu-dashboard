<style>
.rd{font-family:inherit;color:var(--text);}

/* Phase bar */
.rd-phases{display:grid;grid-template-columns:1fr 1fr 1fr;gap:0;border-radius:10px;overflow:hidden;margin-bottom:20px;border:1px solid var(--border);}
.rd-phase{padding:14px 18px;display:flex;flex-direction:column;gap:3px;}
.rd-phase-p1{background:rgba(59,130,246,.12);border-right:1px solid var(--border);}
.rd-phase-p2{background:rgba(234,179,8,.10);border-right:1px solid var(--border);}
.rd-phase-p3{background:rgba(34,197,94,.10);}
.rd-phase-label{font-size:10px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;}
.rd-phase-p1 .rd-phase-label{color:var(--blue);}
.rd-phase-p2 .rd-phase-label{color:var(--yellow);}
.rd-phase-p3 .rd-phase-label{color:var(--green);}
.rd-phase-title{font-size:13px;font-weight:700;}
.rd-phase-sub{font-size:11px;color:var(--dim);}
.rd-phase-bar{height:3px;border-radius:2px;margin-top:6px;}
.rd-phase-p1 .rd-phase-bar{background:var(--blue);}
.rd-phase-p2 .rd-phase-bar{background:var(--yellow);}
.rd-phase-p3 .rd-phase-bar{background:var(--green);}

/* Swimlane */
.rd-swim{display:grid;grid-template-columns:96px 1fr 1fr 1fr;gap:0;border:1px solid var(--border);border-radius:10px;overflow:hidden;margin-bottom:20px;}
.rd-swim-head{background:var(--bg-hover);padding:8px 12px;font-size:10px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:var(--dim);border-bottom:1px solid var(--border);display:flex;align-items:center;}
.rd-swim-head.c1{border-right:1px solid var(--border);}
.rd-swim-head.c2{border-right:1px solid var(--border);color:var(--blue);}
.rd-swim-head.c3{border-right:1px solid var(--border);color:var(--yellow);}
.rd-swim-head.c4{color:var(--green);}
.rd-swim-role{background:var(--bg-card);padding:12px 10px;border-right:1px solid var(--border);border-bottom:1px solid var(--border);display:flex;flex-direction:column;align-items:center;justify-content:flex-start;gap:4px;padding-top:14px;}
.rd-swim-role:last-of-type{border-bottom:none;}
.rd-swim-emoji{font-size:18px;}
.rd-swim-role-name{font-size:10px;font-weight:600;color:var(--dim);text-align:center;line-height:1.3;}
.rd-swim-cell{padding:10px;border-bottom:1px solid var(--border);border-right:1px solid var(--border);vertical-align:top;background:var(--bg);}
.rd-swim-cell.last-col{border-right:none;}
.rd-swim-cell.last-row{border-bottom:none;}
.rd-swim-cell.last-row.last-col{border-right:none;border-bottom:none;}

/* Task cards */
.rd-task{background:var(--bg-card);border:1px solid var(--border);border-radius:7px;padding:8px 10px;margin-bottom:6px;}
.rd-task:last-child{margin-bottom:0;}
.rd-task-name{font-size:12px;font-weight:600;margin-bottom:4px;line-height:1.4;}
.rd-task-meta{display:flex;flex-wrap:wrap;gap:4px;align-items:center;}
.rd-dur{font-size:10px;padding:2px 7px;border-radius:4px;background:var(--bg-hover);color:var(--dim);font-weight:500;}
.risk-r{display:inline-block;width:7px;height:7px;border-radius:50%;background:#ef4444;flex-shrink:0;}
.risk-y{display:inline-block;width:7px;height:7px;border-radius:50%;background:#eab308;flex-shrink:0;}
.risk-g{display:inline-block;width:7px;height:7px;border-radius:50%;background:#22c55e;flex-shrink:0;}
.rd-task-p1{border-left:3px solid var(--blue);}
.rd-task-p2{border-left:3px solid var(--yellow);}
.rd-task-p3{border-left:3px solid var(--green);}

/* Decision points */
.rd-decisions{margin-bottom:20px;}
.rd-decisions-title{font-size:11px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:var(--dim);margin-bottom:10px;}
.rd-dec-row{display:flex;align-items:stretch;gap:0;overflow-x:auto;padding-bottom:4px;}
.rd-dec-item{display:flex;flex-direction:column;align-items:center;min-width:130px;flex:1;}
.rd-dec-dot{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;z-index:1;flex-shrink:0;}
.rd-dec-dot-blue{background:rgba(59,130,246,.2);border:2px solid var(--blue);color:var(--blue);}
.rd-dec-dot-yellow{background:rgba(234,179,8,.2);border:2px solid var(--yellow);color:var(--yellow);}
.rd-dec-dot-green{background:rgba(34,197,94,.2);border:2px solid var(--green);color:var(--green);}
.rd-dec-line{flex:1;height:2px;background:var(--border);margin:13px -1px 0;z-index:0;}
.rd-dec-label{font-size:11px;font-weight:600;margin-top:6px;text-align:center;}
.rd-dec-sub{font-size:10px;color:var(--dim);text-align:center;line-height:1.4;margin-top:2px;}
.rd-dec-badge{font-size:9px;padding:2px 7px;border-radius:4px;margin-top:4px;font-weight:700;}
.rd-dec-badge-go{background:rgba(34,197,94,.15);color:var(--green);}
.rd-dec-badge-check{background:rgba(234,179,8,.15);color:var(--yellow);}

/* Risk register */
.rd-risks{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:20px;}
.rd-risk-card{background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:12px 14px;}
.rd-risk-header{display:flex;align-items:center;gap:8px;margin-bottom:6px;}
.rd-risk-sev{font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px;}
.rd-risk-sev-h{background:rgba(239,68,68,.15);color:#ef4444;}
.rd-risk-sev-m{background:rgba(234,179,8,.15);color:var(--yellow);}
.rd-risk-sev-l{background:rgba(34,197,94,.15);color:var(--green);}
.rd-risk-name{font-size:12px;font-weight:600;}
.rd-risk-desc{font-size:11px;color:var(--muted);margin-bottom:6px;line-height:1.5;}
.rd-risk-mit{font-size:10px;color:var(--dim);display:flex;align-items:flex-start;gap:5px;}
.rd-risk-mit::before{content:"→";color:var(--blue);flex-shrink:0;}

.rd-section-title{font-size:11px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:var(--dim);margin-bottom:10px;display:flex;align-items:center;gap:6px;}
.rd-section-title::before{content:"";display:inline-block;width:3px;height:12px;border-radius:2px;background:var(--blue);}

@media(max-width:768px){
  .rd-phases{grid-template-columns:1fr;}
  .rd-swim{grid-template-columns:72px 1fr;}
  .rd-risks{grid-template-columns:1fr;}
  .rd-dec-item{min-width:100px;}
}
</style>

<div class="rd">

<!-- Phase bar -->
<div class="rd-phases">
  <div class="rd-phase rd-phase-p1">
    <div class="rd-phase-label">Phase 1 · 0 – 6 月</div>
    <div class="rd-phase-title">單店驗證</div>
    <div class="rd-phase-sub">跑通流程、確認損益</div>
    <div class="rd-phase-bar"></div>
  </div>
  <div class="rd-phase rd-phase-p2">
    <div class="rd-phase-label">Phase 2 · 6 – 18 月</div>
    <div class="rd-phase-title">標準化輸出</div>
    <div class="rd-phase-sub">SOP 定版、供應鏈、培訓體系</div>
    <div class="rd-phase-bar"></div>
  </div>
  <div class="rd-phase rd-phase-p3">
    <div class="rd-phase-label">Phase 3 · 18 月+</div>
    <div class="rd-phase-title">規模化</div>
    <div class="rd-phase-sub">設備租賃包、系統授權、更多主理人</div>
    <div class="rd-phase-bar"></div>
  </div>
</div>

<!-- Decision points -->
<div class="rd-decisions">
  <div class="rd-section-title">關鍵決策點（Go / No-Go）</div>
  <div class="rd-dec-row">
    <div class="rd-dec-item">
      <div style="display:flex;align-items:center;width:100%;">
        <div class="rd-dec-dot rd-dec-dot-blue">M1</div>
        <div class="rd-dec-line"></div>
      </div>
      <div class="rd-dec-label">選址定案</div>
      <div class="rd-dec-sub">競業分析<br>租金試算</div>
      <div class="rd-dec-badge rd-dec-badge-go">GO / STOP</div>
    </div>
    <div class="rd-dec-item">
      <div style="display:flex;align-items:center;width:100%;">
        <div class="rd-dec-dot rd-dec-dot-blue">M3</div>
        <div class="rd-dec-line"></div>
      </div>
      <div class="rd-dec-label">菜單驗證</div>
      <div class="rd-dec-sub">毛利率確認<br>出餐速度測試</div>
      <div class="rd-dec-badge rd-dec-badge-check">CHECK</div>
    </div>
    <div class="rd-dec-item">
      <div style="display:flex;align-items:center;width:100%;">
        <div class="rd-dec-dot rd-dec-dot-yellow">M6</div>
        <div class="rd-dec-line"></div>
      </div>
      <div class="rd-dec-label">損益達標</div>
      <div class="rd-dec-sub">進入Phase 2<br>或調整模型</div>
      <div class="rd-dec-badge rd-dec-badge-go">GO / PIVOT</div>
    </div>
    <div class="rd-dec-item">
      <div style="display:flex;align-items:center;width:100%;">
        <div class="rd-dec-dot rd-dec-dot-yellow">M12</div>
        <div class="rd-dec-line"></div>
      </div>
      <div class="rd-dec-label">SOP 可複製驗證</div>
      <div class="rd-dec-sub">新人14天上手<br>品質一致性</div>
      <div class="rd-dec-badge rd-dec-badge-check">CHECK</div>
    </div>
    <div class="rd-dec-item">
      <div style="display:flex;align-items:center;width:100%;">
        <div class="rd-dec-dot rd-dec-dot-green">M18</div>
        <div class="rd-dec-line" style="visibility:hidden;"></div>
      </div>
      <div class="rd-dec-label">第一個外部主理人</div>
      <div class="rd-dec-sub">模型對外輸出<br>進入Phase 3</div>
      <div class="rd-dec-badge rd-dec-badge-go">GO / SCALE</div>
    </div>
  </div>
</div>

<!-- Swimlane -->
<div class="rd-section-title" style="margin-bottom:10px;">誰做什麼 · 什麼時候 · 多久</div>
<div class="rd-swim">
  <!-- Header row -->
  <div class="rd-swim-head c1">角色</div>
  <div class="rd-swim-head c2">Phase 1 &nbsp;0–6月</div>
  <div class="rd-swim-head c3">Phase 2 &nbsp;6–18月</div>
  <div class="rd-swim-head c4">Phase 3 &nbsp;18月+</div>

  <!-- Row: 主理人 -->
  <div class="rd-swim-role">
    <div class="rd-swim-emoji">🧑‍💼</div>
    <div class="rd-swim-role-name">主理人</div>
  </div>
  <div class="rd-swim-cell">
    <div class="rd-task rd-task-p1">
      <div class="rd-task-name">選址評估 &amp; 定案</div>
      <div class="rd-task-meta"><span class="rd-dur">4–6週</span><span class="risk-r"></span></div>
    </div>
    <div class="rd-task rd-task-p1">
      <div class="rd-task-name">雙品牌定位確認</div>
      <div class="rd-task-meta"><span class="rd-dur">2–4週</span><span class="risk-y"></span></div>
    </div>
    <div class="rd-task rd-task-p1">
      <div class="rd-task-name">每日營運管理 &amp; 損益追蹤</div>
      <div class="rd-task-meta"><span class="rd-dur">持續</span><span class="risk-y"></span></div>
    </div>
    <div class="rd-task rd-task-p1">
      <div class="rd-task-name">反饋問題回報系統方</div>
      <div class="rd-task-meta"><span class="rd-dur">持續</span><span class="risk-g"></span></div>
    </div>
  </div>
  <div class="rd-swim-cell">
    <div class="rd-task rd-task-p2">
      <div class="rd-task-name">執行 &amp; 驗證最終 SOP</div>
      <div class="rd-task-meta"><span class="rd-dur">3個月</span><span class="risk-y"></span></div>
    </div>
    <div class="rd-task rd-task-p2">
      <div class="rd-task-name">培訓首批新員工</div>
      <div class="rd-task-meta"><span class="rd-dur">持續</span><span class="risk-y"></span></div>
    </div>
    <div class="rd-task rd-task-p2">
      <div class="rd-task-name">雙品牌社群 &amp; 外送推廣</div>
      <div class="rd-task-meta"><span class="rd-dur">持續</span><span class="risk-y"></span></div>
    </div>
  </div>
  <div class="rd-swim-cell last-col">
    <div class="rd-task rd-task-p3">
      <div class="rd-task-name">協助複製模型輸出</div>
      <div class="rd-task-meta"><span class="rd-dur">持續</span><span class="risk-g"></span></div>
    </div>
    <div class="rd-task rd-task-p3">
      <div class="rd-task-name">評估第二店可行性</div>
      <div class="rd-task-meta"><span class="rd-dur">6個月+</span><span class="risk-y"></span></div>
    </div>
  </div>

  <!-- Row: 系統方 -->
  <div class="rd-swim-role">
    <div class="rd-swim-emoji">⚙️</div>
    <div class="rd-swim-role-name">系統方<br>(Jeff)</div>
  </div>
  <div class="rd-swim-cell">
    <div class="rd-task rd-task-p1">
      <div class="rd-task-name">設備安裝 &amp; 調試</div>
      <div class="rd-task-meta"><span class="rd-dur">3–4週</span><span class="risk-r"></span></div>
    </div>
    <div class="rd-task rd-task-p1">
      <div class="rd-task-name">初版 SOP 制定</div>
      <div class="rd-task-meta"><span class="rd-dur">6–8週</span><span class="risk-y"></span></div>
    </div>
    <div class="rd-task rd-task-p1">
      <div class="rd-task-name">控制系統 &amp; UI 建立</div>
      <div class="rd-task-meta"><span class="rd-dur">2個月</span><span class="risk-y"></span></div>
    </div>
    <div class="rd-task rd-task-p1">
      <div class="rd-task-name">設備異常支援 SLA</div>
      <div class="rd-task-meta"><span class="rd-dur">持續</span><span class="risk-r"></span></div>
    </div>
  </div>
  <div class="rd-swim-cell">
    <div class="rd-task rd-task-p2">
      <div class="rd-task-name">SOP 定版 &amp; 文件化</div>
      <div class="rd-task-meta"><span class="rd-dur">2個月</span><span class="risk-y"></span></div>
    </div>
    <div class="rd-task rd-task-p2">
      <div class="rd-task-name">供應鏈建立 &amp; 談判</div>
      <div class="rd-task-meta"><span class="rd-dur">6個月</span><span class="risk-r"></span></div>
    </div>
    <div class="rd-task rd-task-p2">
      <div class="rd-task-name">培訓體系建立</div>
      <div class="rd-task-meta"><span class="rd-dur">3個月</span><span class="risk-y"></span></div>
    </div>
    <div class="rd-task rd-task-p2">
      <div class="rd-task-name">設備 v2 優化</div>
      <div class="rd-task-meta"><span class="rd-dur">4個月</span><span class="risk-y"></span></div>
    </div>
  </div>
  <div class="rd-swim-cell last-col">
    <div class="rd-task rd-task-p3">
      <div class="rd-task-name">設備租賃包設計</div>
      <div class="rd-task-meta"><span class="rd-dur">2個月</span><span class="risk-y"></span></div>
    </div>
    <div class="rd-task rd-task-p3">
      <div class="rd-task-name">系統授權模型</div>
      <div class="rd-task-meta"><span class="rd-dur">3個月</span><span class="risk-y"></span></div>
    </div>
    <div class="rd-task rd-task-p3">
      <div class="rd-task-name">新主理人導入支援</div>
      <div class="rd-task-meta"><span class="rd-dur">持續</span><span class="risk-g"></span></div>
    </div>
  </div>

  <!-- Row: 現場人員 -->
  <div class="rd-swim-role">
    <div class="rd-swim-emoji">👨‍🍳</div>
    <div class="rd-swim-role-name">現場<br>人員</div>
  </div>
  <div class="rd-swim-cell">
    <div class="rd-task rd-task-p1">
      <div class="rd-task-name">崗位 SOP 培訓</div>
      <div class="rd-task-meta"><span class="rd-dur">2週</span><span class="risk-y"></span></div>
    </div>
    <div class="rd-task rd-task-p1">
      <div class="rd-task-name">執行出餐流程、回報問題</div>
      <div class="rd-task-meta"><span class="rd-dur">持續</span><span class="risk-g"></span></div>
    </div>
  </div>
  <div class="rd-swim-cell">
    <div class="rd-task rd-task-p2">
      <div class="rd-task-name">跨崗位輪替訓練</div>
      <div class="rd-task-meta"><span class="rd-dur">1個月</span><span class="risk-y"></span></div>
    </div>
    <div class="rd-task rd-task-p2">
      <div class="rd-task-name">執行最終版 SOP</div>
      <div class="rd-task-meta"><span class="rd-dur">持續</span><span class="risk-g"></span></div>
    </div>
  </div>
  <div class="rd-swim-cell last-col">
    <div class="rd-task rd-task-p3">
      <div class="rd-task-name">協助培訓新店人員</div>
      <div class="rd-task-meta"><span class="rd-dur">持續</span><span class="risk-g"></span></div>
    </div>
  </div>

  <!-- Row: 外部夥伴 -->
  <div class="rd-swim-role" style="border-bottom:none;">
    <div class="rd-swim-emoji">🤝</div>
    <div class="rd-swim-role-name">外部<br>夥伴</div>
  </div>
  <div class="rd-swim-cell last-row">
    <div class="rd-task rd-task-p1">
      <div class="rd-task-name">外送平台雙品牌上架</div>
      <div class="rd-task-meta"><span class="rd-dur">2–4週</span><span class="risk-y"></span></div>
    </div>
    <div class="rd-task rd-task-p1">
      <div class="rd-task-name">初期供應商接洽</div>
      <div class="rd-task-meta"><span class="rd-dur">6–8週</span><span class="risk-r"></span></div>
    </div>
  </div>
  <div class="rd-swim-cell last-row">
    <div class="rd-task rd-task-p2">
      <div class="rd-task-name">供應鏈框架協議</div>
      <div class="rd-task-meta"><span class="rd-dur">3個月</span><span class="risk-r"></span></div>
    </div>
    <div class="rd-task rd-task-p2">
      <div class="rd-task-name">雙品牌聯合推廣</div>
      <div class="rd-task-meta"><span class="rd-dur">持續</span><span class="risk-y"></span></div>
    </div>
  </div>
  <div class="rd-swim-cell last-row last-col">
    <div class="rd-task rd-task-p3">
      <div class="rd-task-name">規模採購框架協議</div>
      <div class="rd-task-meta"><span class="rd-dur">持續</span><span class="risk-y"></span></div>
    </div>
    <div class="rd-task rd-task-p3">
      <div class="rd-task-name">融資 / 設備分期支援</div>
      <div class="rd-task-meta"><span class="rd-dur">Phase 3 啟動</span><span class="risk-y"></span></div>
    </div>
  </div>
</div>

<!-- Risk register -->
<div class="rd-section-title">風險清單</div>
<div style="display:flex;gap:8px;margin-bottom:10px;font-size:10px;color:var(--dim);align-items:center;">
  <span class="risk-r"></span>高風險 &nbsp;
  <span class="risk-y"></span>中風險 &nbsp;
  <span class="risk-g"></span>低風險
</div>
<div class="rd-risks">
  <div class="rd-risk-card">
    <div class="rd-risk-header"><span class="rd-risk-sev rd-risk-sev-h">高</span><span class="rd-risk-name">選址失誤 → 客流不足</span></div>
    <div class="rd-risk-desc">位置客流量低估，試營運期間無法達到損益平衡，資金提前耗盡。</div>
    <div class="rd-risk-mit">提前做3個月競業流量分析；設定試營運90天評估關卡；預留6個月備用金。</div>
  </div>
  <div class="rd-risk-card">
    <div class="rd-risk-header"><span class="rd-risk-sev rd-risk-sev-h">高</span><span class="rd-risk-name">設備可靠性不足 → 營運中斷</span></div>
    <div class="rd-risk-desc">自製設備在高頻使用下出現故障，導致出餐停擺，嚴重影響口碑與營收。</div>
    <div class="rd-risk-mit">建立備機庫存；簽訂4小時內維修 SLA；Phase 1 保留每月設備巡檢。</div>
  </div>
  <div class="rd-risk-card">
    <div class="rd-risk-header"><span class="rd-risk-sev rd-risk-sev-m">中</span><span class="rd-risk-name">雙品牌切換混亂 → 出餐錯誤</span></div>
    <div class="rd-risk-desc">午晚餐品牌切換時，備料區與設備共用造成人員混淆，出錯率上升。</div>
    <div class="rd-risk-mit">嚴格時段分離（中間30分鐘緩衝）；視覺標識區分兩品牌區域；SOP 分冊管理。</div>
  </div>
  <div class="rd-risk-card">
    <div class="rd-risk-header"><span class="rd-risk-sev rd-risk-sev-m">中</span><span class="rd-risk-name">人員流動高 → 培訓成本失控</span></div>
    <div class="rd-risk-desc">餐飲業人員流動率本就偏高，若SOP複雜，每次替換人員成本過高。</div>
    <div class="rd-risk-mit">SOP 設計以「14天上手」為目標；影片化培訓材料；崗位輪替降低單點依賴。</div>
  </div>
  <div class="rd-risk-card">
    <div class="rd-risk-header"><span class="rd-risk-sev rd-risk-sev-m">中</span><span class="rd-risk-name">供應鏈不穩定 → 缺貨/漲價</span></div>
    <div class="rd-risk-desc">核心食材單一供應商、季節性缺貨或價格波動，直接衝擊毛利與出餐能力。</div>
    <div class="rd-risk-mit">主副供應商雙軌制；關鍵食材保留7天安全庫存；每季重談合約鎖定年度價格。</div>
  </div>
  <div class="rd-risk-card">
    <div class="rd-risk-header"><span class="rd-risk-sev rd-risk-sev-m">中</span><span class="rd-risk-name">外送平台競爭 → 曝光不足</span></div>
    <div class="rd-risk-desc">外送平台演算法競爭激烈，新店初期評價少、排名低，前3個月獲客成本極高。</div>
    <div class="rd-risk-mit">雙品牌同時上架倍增曝光；前3個月優惠策略衝評價；社群私域引流降低平台依賴。</div>
  </div>
  <div class="rd-risk-card">
    <div class="rd-risk-header"><span class="rd-risk-sev rd-risk-sev-l">低</span><span class="rd-risk-name">SOP 被競業抄襲</span></div>
    <div class="rd-risk-desc">標準化SOP文件外流，競業直接複製模型，降低差異化優勢。</div>
    <div class="rd-risk-mit">核心優勢在設備（難以複製）而非文件；SOP 文件分級管理；技術護城河持續加深。</div>
  </div>
  <div class="rd-risk-card">
    <div class="rd-risk-header"><span class="rd-risk-sev rd-risk-sev-l">低</span><span class="rd-risk-name">資本需求在 Phase 3 放大</span></div>
    <div class="rd-risk-desc">規模化需要製造更多設備、提供租賃，資本需求快速增加而現金流滯後。</div>
    <div class="rd-risk-mit">Phase 2 就開始建立融資管道；設備採租賃優先於買斷；控制每月新增主理人數量。</div>
  </div>
</div>

</div>