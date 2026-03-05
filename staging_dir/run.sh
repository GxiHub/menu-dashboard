#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# shellcheck disable=SC1091
source venv/bin/activate

echo "==> 升級 pip / setuptools（避免抓到需要編譯的套件）"
python -m pip install --upgrade pip setuptools

echo "==> 固定 wheel 版本（避免 wheel 與 packaging 版本衝突）"
python -m pip install --upgrade "wheel==0.45.1"

echo "==> 安裝套件（偏好使用 wheel）"
pip install --prefer-binary -r requirements.txt

echo "==> 啟動 Dashboard：http://localhost:8501"
python -m streamlit run dashboard/dashboard.py --server.port 8501
