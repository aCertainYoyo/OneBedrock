"""
OneBedrock Launcher — Desktop Entry Point.
Starts the OneBedrock core backend server and initializes the native desktop window.
"""

import sys
import os
import time
import socket
import threading
import webbrowser

from onebedrock_core.server import run_server

PORT = 42800

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def start_backend():
    if not is_port_in_use(PORT):
        t = threading.Thread(target=run_server, args=(PORT,), daemon=True)
        t.start()
        time.sleep(0.5)

def main():
    print("=" * 60)
    print("           ONEBEDROCK — MINECRAFT BEDROCK CLIENT            ")
    print("      PolyGlass Frosted UI • Xbox Live / Bedrock Only       ")
    print("=" * 60)

    start_backend()
    app_url = f"http://127.0.0.1:{PORT}"
    print(f"[*] Core engine initialized at {app_url}")

    # Try launching native WebView2 desktop window via pywebview
    try:
        import webview
        print("[*] Launching native OneBedrock desktop window...")
        window = webview.create_window(
            title="OneBedrock — Minecraft Bedrock Client",
            url=app_url,
            width=1280,
            height=820,
            min_size=(1024, 680),
            background_color="#11171C"
        )
        webview.start(debug=False)
    except Exception as e:
        print(f"[!] Desktop window manager unavailable ({e}). Opening in default browser...")
        webbrowser.open(app_url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[*] Shutting down OneBedrock.")

if __name__ == "__main__":
    main()
