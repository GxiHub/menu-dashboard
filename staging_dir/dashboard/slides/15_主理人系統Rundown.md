<style>
.sm{font-family:inherit;color:var(--text);}

/* Section header */
.sm-sec{margin-bottom:16px;}
.sm-sec-head{display:flex;align-items:center;gap:8px;margin-bottom:10px;padding:8px 14px;border-radius:8px;cursor:default;}
.sm-sec-icon{font-size:16px;}
.sm-sec-title{font-size:13px;font-weight:700;letter-spacing:.3px;}
.sm-sec-count{font-size:10px;padding:2px 8px;border-radius:10px;font-weight:600;margin-left:auto;}

.sm-hw .sm-sec-head{background:rgba(59,130,246,.10);border:1px solid rgba(59,130,246,.25);}
.sm-hw .sm-sec-title{color:var(--blue);}
.sm-hw .sm-sec-count{background:rgba(59,130,246,.15);color:var(--blue);}

.sm-sw .sm-sec-head{background:rgba(168,85,247,.10);border:1px solid rgba(168,85,247,.25);}
.sm-sw .sm-sec-title{color:#a855f7;}
.sm-sw .sm-sec-count{background:rgba(168,85,247,.15);color:#a855f7;}

.sm-flow .sm-sec-head{background:rgba(34,197,94,.10);border:1px solid rgba(34,197,94,.25);}
.sm-flow .sm-sec-title{color:var(--green);}
.sm-flow .sm-sec-count{background:rgba(34,197,94,.15);color:var(--green);}

.sm-sop .sm-sec-head{background:rgba(234,179,8,.10);border:1px solid rgba(234,179,8,.25);}
.sm-sop .sm-sec-title{color:var(--yellow);}
.sm-sop .sm-sec-count{background:rgba(234,179,8,.15);color:var(--yellow);}

.sm-biz .sm-sec-head{background:rgba(249,115,22,.10);border:1px solid rgba(249,115,22,.25);}
.sm-biz .sm-sec-title{color:#f97316;}
.sm-biz .sm-sec-count{background:rgba(249,115,22,.15);color:#f97316;}

/* Items grid */
.sm-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;}

/* Item card */
.sm-item{background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:10px 12px;display:flex;align-items:flex-start;gap:10px;transition:border-color .15s;}

/* Checkbox */
.sm-chk{width:18px;height:18px;border-radius:5px;border:2px solid var(--border);flex-shrink:0;margin-top:1px;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all .15s;}
.sm-item.done .sm-chk{background:var(--green);border-color:var(--green);}
.sm-item.done .sm-chk::after{content:"✓";color:#fff;font-size:11px;font-weight:800;}
.sm-item.done{border-color:rgba(34,197,94,.3);opacity:.7;}
.sm-item.done .sm-name{text-decoration:line-through;color:var(--dim);}

/* Item content */
.sm-body{flex:1;min-width:0;}
.sm-name{font-size:12px;font-weight:600;line-height:1.4;margin-bottom:4px;}
.sm-desc{font-size:10px;color:var(--dim);line-height:1.4;margin-bottom:6px;}
.sm-tags{display:flex;flex-wrap:wrap;gap:4px;}

/* Relation tags */
.sm-tag{font-size:9px;padding:2px 7px;border-radius:4px;font-weight:600;white-space:nowrap;}
.sm-tag-hw{background:rgba(59,130,246,.12);color:var(--blue);}
.sm-tag-sw{background:rgba(168,85,247,.12);color:#a855f7;}
.sm-tag-flow{background:rgba(34,197,94,.12);color:var(--green);}
.sm-tag-sop{background:rgba(234,179,8,.12);color:var(--yellow);}
.sm-tag-biz{background:rgba(249,115,22,.12);color:#f97316;}

/* Flow diagram */
.sm-pipe{display:flex;align-items:center;gap:0;margin-bottom:20px;padding:14px 16px;background:var(--bg-card);border:1px solid var(--border);border-radius:10px;overflow-x:auto;}
.sm-pipe-step{display:flex;flex-direction:column;align-items:center;min-width:90px;flex:1;}
.sm-pipe-icon{font-size:22px;margin-bottom:4px;}
.sm-pipe-label{font-size:11px;font-weight:700;text-align:center;}
.sm-pipe-sub{font-size:9px;color:var(--dim);text-align:center;margin-top:2px;}
.sm-pipe-arrow{font-size:16px;color:var(--dim);flex-shrink:0;margin:0 2px;}

/* Legend */
.sm-legend{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:16px;padding:8px 14px;background:var(--bg-card);border:1px solid var(--border);border-radius:8px;font-size:10px;color:var(--dim);}
.sm-legend-item{display:flex;align-items:center;gap:5px;}
.sm-legend-dot{width:10px;height:10px;border-radius:3px;flex-shrink:0;}
.sm-legend-dot.hw{background:rgba(59,130,246,.5);}
.sm-legend-dot.sw{background:rgba(168,85,247,.5);}
.sm-legend-dot.flow{background:rgba(34,197,94,.5);}
.sm-legend-dot.sop{background:rgba(234,179,8,.5);}
.sm-legend-dot.biz{background:rgba(249,115,22,.5);}

/* Summary bar */
.sm-summary{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-bottom:20px;}
.sm-stat{text-align:center;padding:10px 8px;border-radius:8px;border:1px solid var(--border);background:var(--bg-card);}
.sm-stat-num{font-size:20px;font-weight:800;line-height:1;}
.sm-stat-label{font-size:9px;color:var(--dim);margin-top:4px;font-weight:600;letter-spacing:.3px;}
.sm-stat-hw .sm-stat-num{color:var(--blue);}
.sm-stat-sw .sm-stat-num{color:#a855f7;}
.sm-stat-flow .sm-stat-num{color:var(--green);}
.sm-stat-sop .sm-stat-num{color:var(--yellow);}
.sm-stat-biz .sm-stat-num{color:#f97316;}

/* Two-column layout */
.sm-cols{display:grid;grid-template-columns:1fr 1fr;gap:20px;}

@media(max-width:768px){
  .sm-grid{grid-template-columns:1fr;}
  .sm-cols{grid-template-columns:1fr;}
  .sm-summary{grid-template-columns:repeat(3,1fr);}
  .sm-pipe-step{min-width:70px;}
}
</style>

<div class="sm">

<!-- Title -->
<div style="text-align:center;margin-bottom:20px;">
  <div style="font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--dim);margin-bottom:4px;">SYSTEM MAP</div>
  <div style="font-size:18px;font-weight:800;">主理人效率餐飲系統 · 全局建置確認</div>
  <div style="font-size:11px;color:var(--dim);margin-top:4px;">軟體 × 硬體 × 流程 × SOP × 商業｜關聯追蹤 + 完成度確認</div>
</div>

<!-- Summary stats -->
<div class="sm-summary">
  <div class="sm-stat sm-stat-hw"><div class="sm-stat-num">6</div><div class="sm-stat-label">硬體項目</div></div>
  <div class="sm-stat sm-stat-sw"><div class="sm-stat-num">7</div><div class="sm-stat-label">軟體模組</div></div>
  <div class="sm-stat sm-stat-flow"><div class="sm-stat-num">5</div><div class="sm-stat-label">營運流程</div></div>
  <div class="sm-stat sm-stat-sop"><div class="sm-stat-num">5</div><div class="sm-stat-label">SOP 文件</div></div>
  <div class="sm-stat sm-stat-biz"><div class="sm-stat-num">5</div><div class="sm-stat-label">商業模組</div></div>
</div>

<!-- Legend -->
<div class="sm-legend">
  <div style="font-weight:700;color:var(--text);">關聯標籤：</div>
  <div class="sm-legend-item"><div class="sm-legend-dot hw"></div>硬體</div>
  <div class="sm-legend-item"><div class="sm-legend-dot sw"></div>軟體</div>
  <div class="sm-legend-item"><div class="sm-legend-dot flow"></div>流程</div>
  <div class="sm-legend-item"><div class="sm-legend-dot sop"></div>SOP</div>
  <div class="sm-legend-item"><div class="sm-legend-dot biz"></div>商業</div>
  <div style="margin-left:auto;font-weight:600;">☐ 未完成 &nbsp; ☑ 已完成</div>
</div>

<!-- Core flow pipeline -->
<div style="font-size:11px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:var(--dim);margin-bottom:8px;display:flex;align-items:center;gap:6px;"><span style="display:inline-block;width:3px;height:12px;border-radius:2px;background:var(--green);"></span>核心營運流程</div>
<div class="sm-pipe">
  <div class="sm-pipe-step">
    <div class="sm-pipe-icon">📱</div>
    <div class="sm-pipe-label">點餐</div>
    <div class="sm-pipe-sub">POS 收銀台<br>開始計時</div>
  </div>
  <div class="sm-pipe-arrow">→</div>
  <div class="sm-pipe-step">
    <div class="sm-pipe-icon">📺</div>
    <div class="sm-pipe-label">撿料站</div>
    <div class="sm-pipe-sub">KDS 螢幕<br>備料確認</div>
  </div>
  <div class="sm-pipe-arrow">→</div>
  <div class="sm-pipe-step">
    <div class="sm-pipe-icon">🍲</div>
    <div class="sm-pipe-label">滷鍋站</div>
    <div class="sm-pipe-sub">自動升降機<br>滷製完成</div>
  </div>
  <div class="sm-pipe-arrow">→</div>
  <div class="sm-pipe-step">
    <div class="sm-pipe-icon">✅</div>
    <div class="sm-pipe-label">出餐檢核</div>
    <div class="sm-pipe-sub">逐項確認<br>打包完成</div>
  </div>
  <div class="sm-pipe-arrow">→</div>
  <div class="sm-pipe-step">
    <div class="sm-pipe-icon">📊</div>
    <div class="sm-pipe-label">數據回流</div>
    <div class="sm-pipe-sub">Dashboard<br>即時監控</div>
  </div>
</div>

<!-- Two column layout: Hardware + Software -->
<div class="sm-cols">

<!-- ===== HARDWARE ===== -->
<div class="sm-sec sm-hw">
  <div class="sm-sec-head">
    <span class="sm-sec-icon">🔧</span>
    <span class="sm-sec-title">硬體 Hardware</span>
    <span class="sm-sec-count">6 項</span>
  </div>
  <div class="sm-grid" style="grid-template-columns:1fr;">
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">自動升降滷台</div>
        <div class="sm-desc">電動升降機構，控制滷製時間與溫度</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-flow">滷鍋站</span>
          <span class="sm-tag sm-tag-sw">KDS 派單</span>
          <span class="sm-tag sm-tag-sop">設備操作 SOP</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">POS 收銀設備</div>
        <div class="sm-desc">觸控螢幕 + 錢箱 + 出單機</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-flow">點餐</span>
          <span class="sm-tag sm-tag-sw">POS 系統</span>
          <span class="sm-tag sm-tag-sw">財務系統</span>
          <span class="sm-tag sm-tag-biz">雙品牌收銀</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">撿料站螢幕（KDS）</div>
        <div class="sm-desc">撿料工位顯示器，即時接收訂單</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-flow">撿料站</span>
          <span class="sm-tag sm-tag-sw">KDS 派單</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">滷鍋站螢幕（KDS）</div>
        <div class="sm-desc">滷鍋工位顯示器，顯示滷製狀態</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-flow">滷鍋站</span>
          <span class="sm-tag sm-tag-sw">KDS 派單</span>
          <span class="sm-tag sm-tag-hw">自動升降滷台</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">出餐站螢幕</div>
        <div class="sm-desc">出餐檢核用，顯示打包清單</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-flow">出餐檢核</span>
          <span class="sm-tag sm-tag-sw">檢核系統</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">網路基礎設施</div>
        <div class="sm-desc">路由器 / 交換器 / Wi-Fi，串接所有設備</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-sw">全系統</span>
          <span class="sm-tag sm-tag-hw">所有螢幕</span>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ===== SOFTWARE ===== -->
<div class="sm-sec sm-sw">
  <div class="sm-sec-head">
    <span class="sm-sec-icon">💻</span>
    <span class="sm-sec-title">軟體 Software</span>
    <span class="sm-sec-count">7 項</span>
  </div>
  <div class="sm-grid" style="grid-template-columns:1fr;">
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">POS 收銀系統</div>
        <div class="sm-desc">點餐介面、品項管理、結帳、開始計時</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-hw">POS 設備</span>
          <span class="sm-tag sm-tag-flow">點餐</span>
          <span class="sm-tag sm-tag-sw">財務系統</span>
          <span class="sm-tag sm-tag-sw">CRM</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">KDS 工作站派單系統</div>
        <div class="sm-desc">訂單自動分派到撿料站 / 滷鍋站 / 出餐站</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-hw">撿料站螢幕</span>
          <span class="sm-tag sm-tag-hw">滷鍋站螢幕</span>
          <span class="sm-tag sm-tag-flow">撿料站</span>
          <span class="sm-tag sm-tag-flow">滷鍋站</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">出餐檢核系統</div>
        <div class="sm-desc">打包清單逐項確認，防止漏裝</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-hw">出餐站螢幕</span>
          <span class="sm-tag sm-tag-flow">出餐檢核</span>
          <span class="sm-tag sm-tag-sop">出餐 SOP</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">財務系統</div>
        <div class="sm-desc">POS 營收自動入帳，每日對帳</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-sw">POS 系統</span>
          <span class="sm-tag sm-tag-sw">Dashboard</span>
          <span class="sm-tag sm-tag-biz">損益追蹤</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">CRM 客戶管理</div>
        <div class="sm-desc">綁定客戶電話，消費紀錄、回購分析</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-sw">POS 系統</span>
          <span class="sm-tag sm-tag-biz">行銷推播</span>
          <span class="sm-tag sm-tag-biz">雙品牌</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">計時追蹤系統</div>
        <div class="sm-desc">全流程計時：點餐→撿料→滷製→出餐</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-flow">全流程</span>
          <span class="sm-tag sm-tag-sw">Dashboard</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">主理人 Dashboard</div>
        <div class="sm-desc">即時監控：營收、效率、庫存、客戶數據</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-sw">財務系統</span>
          <span class="sm-tag sm-tag-sw">CRM</span>
          <span class="sm-tag sm-tag-sw">計時系統</span>
          <span class="sm-tag sm-tag-flow">數據回流</span>
        </div>
      </div>
    </div>
  </div>
</div>

</div><!-- end sm-cols -->

<!-- Two column layout: Flow + SOP -->
<div class="sm-cols" style="margin-top:20px;">

<!-- ===== FLOW ===== -->
<div class="sm-sec sm-flow">
  <div class="sm-sec-head">
    <span class="sm-sec-icon">🔄</span>
    <span class="sm-sec-title">營運流程 Flow</span>
    <span class="sm-sec-count">5 站</span>
  </div>
  <div class="sm-grid" style="grid-template-columns:1fr;">
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">① 點餐流程</div>
        <div class="sm-desc">客戶下單 → POS 建立訂單 → 系統開始計時 → 綁定客戶電話</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-hw">POS 設備</span>
          <span class="sm-tag sm-tag-sw">POS 系統</span>
          <span class="sm-tag sm-tag-sw">CRM</span>
          <span class="sm-tag sm-tag-sop">營運 SOP</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">② 撿料流程</div>
        <div class="sm-desc">KDS 派單 → 撿料手看螢幕備料 → 逐項完成 → 按「確認」流轉</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-hw">撿料站螢幕</span>
          <span class="sm-tag sm-tag-sw">KDS 派單</span>
          <span class="sm-tag sm-tag-sop">出餐 SOP</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">③ 滷製流程</div>
        <div class="sm-desc">接收已備料 → 放入自動升降機 → 滷製完成 → 按「出餐」</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-hw">自動升降滷台</span>
          <span class="sm-tag sm-tag-hw">滷鍋站螢幕</span>
          <span class="sm-tag sm-tag-sw">KDS 派單</span>
          <span class="sm-tag sm-tag-sop">設備操作 SOP</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">④ 出餐檢核</div>
        <div class="sm-desc">系統跳出打包清單 → 逐項確認食材 → 全數打勾 → 完成出餐</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-hw">出餐站螢幕</span>
          <span class="sm-tag sm-tag-sw">檢核系統</span>
          <span class="sm-tag sm-tag-sop">出餐 SOP</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">⑤ 數據回流</div>
        <div class="sm-desc">全程計時數據 + 營收 + 客戶資料 → Dashboard 即時呈現</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-sw">Dashboard</span>
          <span class="sm-tag sm-tag-sw">財務系統</span>
          <span class="sm-tag sm-tag-sw">CRM</span>
          <span class="sm-tag sm-tag-biz">損益追蹤</span>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ===== SOP ===== -->
<div class="sm-sec sm-sop">
  <div class="sm-sec-head">
    <span class="sm-sec-icon">📋</span>
    <span class="sm-sec-title">SOP 文件</span>
    <span class="sm-sec-count">5 份</span>
  </div>
  <div class="sm-grid" style="grid-template-columns:1fr;">
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">出餐流程 SOP</div>
        <div class="sm-desc">備料 → 組裝 → 出餐，每步有標準時間和品質基準</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-flow">撿料站</span>
          <span class="sm-tag sm-tag-flow">滷鍋站</span>
          <span class="sm-tag sm-tag-flow">出餐檢核</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">設備操作 SOP</div>
        <div class="sm-desc">自動升降滷台操作手冊 + 異常處理流程</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-hw">自動升降滷台</span>
          <span class="sm-tag sm-tag-flow">滷鍋站</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">日常營運 SOP</div>
        <div class="sm-desc">開店準備 / 品牌切換 / 交接班 / 打烊收尾</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-flow">點餐</span>
          <span class="sm-tag sm-tag-biz">雙品牌</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">清潔流程 SOP</div>
        <div class="sm-desc">日清 / 週清 / 月清，檢核表管理</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-hw">全設備</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">培訓 SOP</div>
        <div class="sm-desc">14 天上手目標，影片化教材，崗位輪替訓練</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-sw">KDS 操作</span>
          <span class="sm-tag sm-tag-sw">POS 操作</span>
          <span class="sm-tag sm-tag-biz">可複製</span>
        </div>
      </div>
    </div>
  </div>
</div>

</div><!-- end sm-cols -->

<!-- ===== BUSINESS ===== -->
<div class="sm-sec sm-biz" style="margin-top:20px;">
  <div class="sm-sec-head">
    <span class="sm-sec-icon">💼</span>
    <span class="sm-sec-title">商業模組 Business</span>
    <span class="sm-sec-count">5 項</span>
  </div>
  <div class="sm-grid">
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">單店雙品牌模型</div>
        <div class="sm-desc">午餐品牌（高翻桌）+ 晚餐品牌（高毛利），一份租金兩份營收</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-sw">POS 系統</span>
          <span class="sm-tag sm-tag-sop">營運 SOP</span>
          <span class="sm-tag sm-tag-biz">外送平台</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">外送平台雙品牌上架</div>
        <div class="sm-desc">兩個品牌同時上架，倍增曝光與流量</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-biz">雙品牌</span>
          <span class="sm-tag sm-tag-sw">POS 系統</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">供應鏈建立</div>
        <div class="sm-desc">主副供應商雙軌制，核心食材安全庫存</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-sop">出餐 SOP</span>
          <span class="sm-tag sm-tag-sw">財務系統</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">設備租賃模型</div>
        <div class="sm-desc">主理人月租設備，不用一次買斷，降低開店門檻</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-hw">自動升降滷台</span>
          <span class="sm-tag sm-tag-hw">全套 KDS</span>
        </div>
      </div>
    </div>
    <div class="sm-item">
      <div class="sm-chk"></div>
      <div class="sm-body">
        <div class="sm-name">模型可複製驗證</div>
        <div class="sm-desc">SOP + 設備 + 數位系統打包，新主理人可快速導入</div>
        <div class="sm-tags">
          <span class="sm-tag sm-tag-sop">全部 SOP</span>
          <span class="sm-tag sm-tag-sw">全系統</span>
          <span class="sm-tag sm-tag-hw">全設備</span>
        </div>
      </div>
    </div>
  </div>
</div>

</div>
