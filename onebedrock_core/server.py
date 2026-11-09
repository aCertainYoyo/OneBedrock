"""
OneBedrock Local Backend Server.
Provides a REST API to bridge the PolyGlass UI with Bedrock system services,
accounts, packs, and the Minecraft Bedrock launch engine.
"""

import os
import sys
import json
import time
import mimetypes
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from onebedrock_core.auth import BedrockAccountManager
from onebedrock_core.launcher import BedrockLauncher
from onebedrock_core.optimizer import BedrockOptimizer
from onebedrock_core.packs import BedrockPackManager
from onebedrock_core.instances import InstanceManager
from onebedrock_core import browser_service

APP_DIR = Path(__file__).resolve().parent.parent / "onebedrock_app"

class OneBedrockBackend:
    def __init__(self):
        self.auth_mgr = BedrockAccountManager()
        self.launcher = BedrockLauncher()
        self.optimizer = BedrockOptimizer()
        self.pack_mgr = BedrockPackManager()
        self.inst_mgr = InstanceManager()
        self.logs = []

        self.launcher.add_log_listener(self._record_log)

    def _record_log(self, stage: str, message: str):
        self.logs.append({
            "stage": stage,
            "message": message,
            "timestamp": time.time()
        })
        if len(self.logs) > 200:
            self.logs = self.logs[-200:]

backend_instance = OneBedrockBackend()

class OneBedrockRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(APP_DIR), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            self.handle_api_get(path, parse_qs(parsed.query))
        else:
            # Handle Single-Page App routing fallback
            file_path = APP_DIR / path.lstrip("/")
            if not file_path.exists() or file_path.is_dir():
                self.path = "/index.html"
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            payload = {}

        if path.startswith("/api/"):
            self.handle_api_post(path, payload)
        else:
            self.send_error(404, "Not found")

    def _send_json(self, data: dict, status: int = 200):
        res = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(res)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store")
        self.end_headers()
        self.wfile.write(res)

    def handle_api_get(self, path: str, query: dict):
        b = backend_instance
        if path == "/api/status":
            bedrock_info = b.launcher.check_bedrock_installed()
            self._send_json({
                "status": "online",
                "version": "1.0.0",
                "app": "OneBedrock",
                "bedrock": bedrock_info,
                "is_running": b.launcher.is_running,
                "session": b.launcher.current_session
            })
        elif path == "/api/accounts":
            self._send_json({
                "accounts": b.auth_mgr.get_accounts(),
                "active_account": b.auth_mgr.get_active_account()
            })
        elif path == "/api/instances":
            self._send_json({
                "instances": b.inst_mgr.get_instances(),
                "active_instance": b.inst_mgr.get_active_instance()
            })
        elif path == "/api/optimizer":
            self._send_json({
                "metrics": b.optimizer.get_current_metrics(),
                "presets": b.optimizer.get_presets()
            })
        elif path == "/api/packs":
            self._send_json({
                "resource_packs": b.pack_mgr.list_resource_packs(),
                "behavior_packs": b.pack_mgr.list_behavior_packs(),
                "worlds": b.pack_mgr.list_worlds()
            })
        elif path == "/api/browse":
            self._send_json({
                "servers": browser_service.get_servers(),
                "packs": browser_service.get_packs(),
                "news": browser_service.get_news()
            })
        elif path == "/api/logs":
            self._send_json({
                "logs": b.logs
            })
        else:
            self._send_json({"error": "Unknown API endpoint"}, 404)

    def handle_api_post(self, path: str, payload: dict):
        b = backend_instance
        if path == "/api/accounts/switch":
            acc_id = payload.get("id")
            success = b.auth_mgr.set_active_account(acc_id)
            self._send_json({"success": success, "active": b.auth_mgr.get_active_account()})
        elif path == "/api/accounts/add":
            gamertag = payload.get("gamertag", "BedrockPlayer")
            acc = b.auth_mgr.add_local_account(gamertag)
            self._send_json({"success": True, "account": acc})
        elif path == "/api/accounts/device_flow":
            flow = b.auth_mgr.initiate_device_flow()
            self._send_json(flow)
        elif path == "/api/accounts/remove":
            acc_id = payload.get("id")
            success = b.auth_mgr.remove_account(acc_id)
            self._send_json({"success": success})
        elif path == "/api/instances/switch":
            inst_id = payload.get("id")
            success = b.inst_mgr.set_active_instance(inst_id)
            self._send_json({"success": success, "active": b.inst_mgr.get_active_instance()})
        elif path == "/api/instances/create":
            name = payload.get("name", "New Bedrock Instance")
            preset = payload.get("preset", "balanced")
            inst = b.inst_mgr.create_instance(name=name, preset=preset)
            self._send_json({"success": True, "instance": inst})
        elif path == "/api/instances/delete":
            inst_id = payload.get("id")
            success = b.inst_mgr.delete_instance(inst_id)
            self._send_json({"success": success})
        elif path == "/api/optimizer/preset":
            preset_id = payload.get("preset")
            success = b.optimizer.apply_preset(preset_id)
            self._send_json({"success": success, "metrics": b.optimizer.get_current_metrics()})
        elif path == "/api/launch":
            inst = b.inst_mgr.get_active_instance() or {}
            acc = b.auth_mgr.get_active_account() or {}
            server_ip = payload.get("server_ip")
            server_port = int(payload.get("server_port", 19132))
            
            # Apply instance optimization preset before launch
            preset = inst.get("preset", "balanced")
            b.optimizer.apply_preset(preset)
            
            res = b.launcher.launch(
                instance_name=inst.get("name", "Bedrock"),
                gamertag=acc.get("gamertag", "BedrockCrafter"),
                server_ip=server_ip,
                server_port=server_port
            )
            self._send_json(res)
        elif path == "/api/stop":
            summary = b.launcher.stop_session()
            self._send_json({"success": True, "session": summary})
        else:
            self._send_json({"error": "Unknown API endpoint"}, 404)

def run_server(port: int = 42800):
    server = HTTPServer(("127.0.0.1", port), OneBedrockRequestHandler)
    print(f"[OneBedrock] Server running on http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    run_server()
