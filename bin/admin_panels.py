import os
import socket
import http.client
import json
import subprocess
from datetime import datetime
import streamlit as st

BASE_PATH   = "/home/pi53/dashboard"
STAGING_URL = "http://192.168.1.111:8502"
PROD_URL    = "http://192.168.1.111:8501"

# ── helpers ──────────────────────────────────────────────────────────────────

def _run(cmd: str, timeout: int = 20) -> str:
    try:
        p = subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=timeout)
        out = (p.stdout or "").strip()
        err = (p.stderr or "").strip()
        if out and err:
            return out + "\n" + err
        return out or err or "(no output)"
    except subprocess.TimeoutExpired:
        return "[TIMEOUT] " + cmd
    except Exception as e:
        return "[ERROR] " + str(e)


class _UnixConn(http.client.HTTPConnection):
    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        self.sock.connect("/var/run/docker.sock")


def _docker_get(path: str):
    try:
        conn = _UnixConn("localhost")
        conn.request("GET", path)
        r = conn.getresponse()
        return r.status, r.read()
    except Exception as e:
        return 0, str(e).encode()


def _parse_docker_logs(raw: bytes) -> str:
    """解析 Docker multiplexed log stream（每 frame 有 8-byte header）。"""
    lines, i = [], 0
    while i + 8 <= len(raw):
        size = int.from_bytes(raw[i + 4:i + 8], "big")
        i += 8
        lines.append(raw[i:i + size].decode("utf-8", errors="replace").rstrip("\n"))
        i += size
    return "\n".join(lines)


def _http_check(host: str, port: int) -> str:
    try:
        conn = http.client.HTTPConnection(host, port, timeout=5)
        conn.request("GET", "/")
        r = conn.getresponse()
        return str(r.status)
    except Exception as e:
        return f"ERR: {e}"


# ── panels ───────────────────────────────────────────────────────────────────

def panel_healthcheck():
    with st.sidebar.expander("🩺 系統健康檢查", expanded=False):
        st.caption("檢查 PROD / Staging 容器狀態與最近 logs。")
        if st.button("🔄 執行健康檢查", width="stretch", key="btn_hc"):
            results = {}
            for name in ["menu-dashboard", "menu-dashboard-staging"]:
                status, body = _docker_get(f"/containers/{name}/json")
                if status == 200:
                    info  = json.loads(body)
                    state = info.get("State", {})
                    _, log_raw = _docker_get(
                        f"/containers/{name}/logs?stdout=1&stderr=1&tail=30&timestamps=1"
                    )
                    results[name] = {
                        "status":  state.get("Status", "unknown"),
                        "running": state.get("Running", False),
                        "started": state.get("StartedAt", "")[:19].replace("T", " "),
                        "logs":    _parse_docker_logs(log_raw) if isinstance(log_raw, bytes) else str(log_raw),
                    }
                else:
                    results[name] = {
                        "status": "not found", "running": False, "started": "", "logs": ""
                    }
            st.session_state["_hc_ts"]        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state["_hc_results"]   = results
            st.session_state["_hc_prod_http"] = _http_check("127.0.0.1", 8501)
            st.session_state["_hc_stag_http"] = _http_check("127.0.0.1", 8502)

        if st.session_state.get("_hc_ts"):
            st.caption("最後檢查：" + st.session_state["_hc_ts"])
            results   = st.session_state.get("_hc_results", {})
            prod_http = st.session_state.get("_hc_prod_http", "")
            stag_http = st.session_state.get("_hc_stag_http", "")
            for name, r in results.items():
                icon = "🟢" if r["running"] else "🔴"
                st.markdown(f"**{icon} {name}**")
                st.code(f"Status : {r['status']}\nStarted: {r['started']}", language="text")
                if r["logs"]:
                    with st.expander("最近 logs"):
                        st.code(r["logs"], language="text")
            st.markdown(f"**HTTP** — PROD: `{prod_http}` / Staging: `{stag_http}`")


def panel_deploy_manager():
    with st.sidebar.expander("🧩 部署管理 (Staging → PROD)", expanded=False):
        st.caption("在 Staging 確認 OK 後，Promote 到 PROD。")

        prod_ver = _run(
            "cat /home/pi53/dashboard/current/DEPLOYED.txt 2>/dev/null || echo '(無記錄)'",
            timeout=5,
        )
        stag_ver = _run("cat /app/DEPLOYED.txt 2>/dev/null || echo '(無記錄)'", timeout=5)

        st.markdown("**PROD 版本**");    st.code(prod_ver, language="text")
        st.markdown("**Staging 版本**"); st.code(stag_ver, language="text")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Promote to PROD", width="stretch", key="btn_promote"):
                with st.spinner("Promoting..."):
                    out = _run("python3 /host/promote_ui.py", timeout=60)
                st.code(out, language="text")
        with col2:
            if st.button("↩️ Rollback PROD", width="stretch", key="btn_rollback"):
                with st.spinner("Rolling back..."):
                    out = _run("python3 /host/rollback_ui.py", timeout=60)
                st.code(out, language="text")

        st.divider()
        st.caption("Staging: " + STAGING_URL)
        st.caption("PROD:    " + PROD_URL)


def render_all():
    panel_healthcheck()
    panel_deploy_manager()
