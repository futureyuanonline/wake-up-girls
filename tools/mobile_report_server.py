"""移动端检测结果接收器（仅本地临时使用）
Edge 无头模式无法可靠回传 stdout，因此让浏览器把检测结果 POST 回来，落到文件。
用法：python tools/_mtest_server.py 8766
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

OUT = Path(__file__).resolve().parent / "mobile-report.json"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8766


class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n).decode("utf-8", "replace")
        try:
            data = json.loads(raw)
            OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"[report] {len(data.get('pages', []))} pages written -> {OUT}", flush=True)
        except Exception as e:  # noqa: BLE001
            OUT.with_suffix(".raw.txt").write_text(raw, encoding="utf-8")
            print(f"[report] raw saved ({e})", flush=True)
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"listening on http://127.0.0.1:{PORT}/  ->  {OUT}", flush=True)
    HTTPServer(("127.0.0.1", PORT), H).serve_forever()
