from typing import Dict

# 中文 CSV 欄位 -> DB 英文欄位（程式內部統一用英文）
CN_TO_EN: Dict[str, str] = {
    "產品編號": "product_id",
    "產品名稱": "product_name",
    "分類": "category",
    "單位數量": "unit_qty",
    "單位": "unit",
    "保存期限": "shelf_life",
    "單包重量": "purchase_weight",
    "商品單位克數": "unit_weight",
    "商品重量單位": "unit_weight_unit",
    "產品售價": "sale_price",
    "售價備註": "price_note",
    "廠商": "vendor",
    "單位成本": "unit_cost",
    "單包進貨價": "purchase_price",
    "是否現場準備": "is_prepared_on_site",
    "是否菜單品項": "is_menu_item",
    "是否上架": "is_available",
    "備註": "note",
}

EN_TO_CN: Dict[str, str] = {v: k for k, v in CN_TO_EN.items()}
