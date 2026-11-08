#!/usr/bin/env python3
"""Actualiza canales.m3u desde los enlaces AceStream publicados por Ciriaco."""
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

SOURCE = "https://ciriaco.netlify.app/"
OUTPUT = Path(__file__).resolve().parent / "canales.m3u"
HASH = re.compile(r"^acestream://[0-9a-f]{40}$", re.IGNORECASE)
MIN_CHANNELS = 12

def extract(page):
    # Incluye enlaces ocultos en paneles desplegables, igual que el JSON original.
    return page.evaluate("""() => Array.from(document.querySelectorAll('a[href]'))
      .map(a => ({nombre: (a.textContent || a.getAttribute('title') || '').trim(),
                  url: a.getAttribute('href') || ''}))
      .filter(a => a.url.startsWith('acestream://'))""")

def collect():
    gathered = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        try:
            page = browser.new_page(locale="es-ES", viewport={"width": 1366, "height": 900})
            page.goto(SOURCE, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2200)
            gathered.extend(extract(page))
            # Algunos eventos pueden cargarse al desplazarse.
            for _ in range(12):
                page.evaluate("window.scrollBy(0, window.innerHeight * 2)")
                page.wait_for_timeout(280)
                gathered.extend(extract(page))
            # Si los enlaces se añaden al abrir paneles, desplegarlos.
            if len({x["url"] for x in gathered}) < MIN_CHANNELS:
                buttons = page.get_by_text("Ver enlaces", exact=True)
                for i in range(min(buttons.count(), 100)):
                    try:
                        buttons.nth(i).click(timeout=900)
                        gathered.extend(extract(page))
                    except Exception:
                        continue
        finally:
            browser.close()
    return gathered

def normalize(raw):
    unique = {}
    for entry in raw:
        url = str(entry.get("url", "")).strip()
        if not HASH.fullmatch(url):
            continue
        name = re.sub(r"\s+", " ", str(entry.get("nombre") or "Canal AceStream")).strip()
        name = name.replace("\n", " ").replace("\r", " ")
        if not name:
            name = "Canal AceStream"
        unique.setdefault(url.lower(), name)
    return sorted(unique.items(), key=lambda item: (item[1].casefold(), item[0]))

def render(items):
    lines = ["#EXTM3U"]
    for url, name in items:
        title = name.replace('"', "'")
        lines.append(f'#EXTINF:-1 group-title="Ciriaco AceStream",{title}')
        lines.append(url)
    return "\n".join(lines) + "\n"

def previous_count(content):
    return len(re.findall(r"(?m)^acestream://[0-9a-f]{40}\s*$", content))

def main():
    entries = normalize(collect())
    old = OUTPUT.read_text(encoding="utf-8-sig") if OUTPUT.exists() else ""
    old_count = previous_count(old)
    print(f"Encontrados: {len(entries)} enlaces únicos. Lista anterior: {old_count}.")
    if len(entries) < MIN_CHANNELS:
        raise RuntimeError(f"Extracción incompleta ({len(entries)} enlaces); se conserva la lista anterior.")
    if old_count and len(entries) < old_count * 0.30:
        raise RuntimeError("La extracción perdió más del 70 % de enlaces; no se sobrescribe la lista.")
    updated = render(entries)
    if updated == old:
        print("Sin cambios: no se modifica la M3U.")
        return
    OUTPUT.write_text(updated, encoding="utf-8")
    print(f"Actualizada la M3U con {len(entries)} enlaces únicos.")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
