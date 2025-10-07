#!/usr/bin/env python3
"""
Simple local dev server for the election widget.

- Serves the current folder over HTTP (no caching) so the HTML can fetch data.
- Generates data.csv and data.json immediately, then updates them every N seconds.

Usage (PowerShell):
  py .\server.py --port 8080 --interval 30
  # or
  python .\server.py --port 8080 --interval 30

Stop with Ctrl+C.
"""
from __future__ import annotations

import argparse
import csv
import http.server
import json
import os
import random
import socket
import sys
import threading
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "data.csv"
JSON_PATH = ROOT / "data.json"

# Parties and colors consistent with the sample in the app
PARTIES = [
    {"name": "Alpha", "color": "#1f77b4", "base": 120},
    {"name": "Beta",  "color": "#ff7f0e", "base": 100},
    {"name": "Gamma", "color": "#2ca02c", "base": 80},
]

YEARS = ["2020", "2024"]


def new_random_snapshot() -> list[dict]:
    rng = random.Random()
    rows = []
    for p in PARTIES:
        row = {
            "Party": p["name"],
            "Color": p["color"],
        }
        for y in YEARS:
            delta = rng.randint(-5, 5)
            seats = max(0, p["base"] + delta)
            leads = rng.randint(0, 5)
            row[f"{y}_Seats"] = seats
            row[f"{y}_Leads"] = leads
        rows.append(row)
    return rows


def write_csv_and_json(rows: list[dict]) -> None:
    # Ensure root exists (it should) and write in UTF-8
    headers = ["Party", "Color"] + [f"{y}_{suf}" for y in YEARS for suf in ("Seats", "Leads")]

    # Write CSV with consistent header order
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            writer.writerow({h: r.get(h, "") for h in headers})

    # Write JSON matching ELECTION_DATA shape
    data = {
        "years": YEARS,
        "parties": [
            {
                "party": r["Party"],
                "yearly_results": [
                    {"year": y, "seats": int(r.get(f"{y}_Seats", 0)), "leads": int(r.get(f"{y}_Leads", 0))}
                    for y in YEARS
                ],
            }
            for r in rows
        ],
    }
    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class NoCacheRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        # Disable caching so the browser always fetches the latest data
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        # Allow cross-origin GETs so the embed can fetch data from other domains
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_POST(self) -> None:
        # Minimal POST endpoint to save exported embed HTML to the project folder.
        # Only supports same-origin requests from the local page.
        if self.path.rstrip("/") == "/save-embed":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                data = self.rfile.read(length) if length > 0 else b""
                # Treat body as UTF-8 HTML content
                out_path = ROOT / "superdynamic - embed.html"
                out_path.write_bytes(data)
                resp = {"ok": True, "path": str(out_path)}
                body = json.dumps(resp).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                msg = {"ok": False, "error": str(e)}
                body = json.dumps(msg).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            return

        # Fallback for all other POSTs
        self.send_error(404, "Not Found")


def serve(port: int) -> None:
    os.chdir(ROOT)
    # ThreadingHTTPServer is available in Python 3.7+
    try:
        server_cls = http.server.ThreadingHTTPServer  # type: ignore[attr-defined]
    except AttributeError:
        # Fallback (single-threaded) if older Python
        server_cls = http.server.HTTPServer

    with server_cls(("127.0.0.1", port), NoCacheRequestHandler) as httpd:
        sa = httpd.socket.getsockname()
        print(f"Serving {ROOT} at http://{sa[0]}:{sa[1]}/", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


def run_updater(interval: int, stop_evt: threading.Event) -> None:
    # Initial write
    rows = new_random_snapshot()
    write_csv_and_json(rows)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Data initialized", flush=True)

    while not stop_evt.wait(interval):
        try:
            rows = new_random_snapshot()
            write_csv_and_json(rows)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Data updated", flush=True)
        except Exception as e:
            print(f"WARNING: Failed to update data: {e}", file=sys.stderr, flush=True)


def parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Local server + auto-updating data for the election widget")
    ap.add_argument("--port", type=int, default=8080, help="Port to serve on (default: 8080)")
    ap.add_argument("--interval", type=int, default=30, help="Seconds between data updates (default: 30)")
    return ap.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    # Start background updater
    stop_evt = threading.Event()
    t = threading.Thread(target=run_updater, args=(args.interval, stop_evt), daemon=True)
    t.start()

    # Start HTTP server (blocks until Ctrl+C)
    try:
        serve(args.port)
        return 0
    finally:
        stop_evt.set()
        t.join(timeout=2)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
