#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Берём уже готовые объединённые файлы UA_RU_* и
публикуем их как public/blink.m3u и public/full.m3u.
Если вдруг файлов нет — создаём безопасные заглушки,
чтобы GitHub Actions не падал.
"""

import os
import shutil

# Путь к корню репозитория (подняться из scripts/)
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(REPO_ROOT)

OUT_DIR = os.path.join(REPO_ROOT, "public")
os.makedirs(OUT_DIR, exist_ok=True)

# Откуда берём готовые файлы (положи их в корень репо)
SRC_BLINK = os.path.join(REPO_ROOT, "UA_RU_BLINK.m3u")
SRC_FULL  = os.path.join(REPO_ROOT, "UA_RU_FULL.m3u")

DST_BLINK = os.path.join(OUT_DIR, "blink.m3u")
DST_FULL  = os.path.join(OUT_DIR, "full.m3u")

def safe_copy(src, dst, fallback_name):
    if os.path.isfile(src):
        shutil.copyfile(src, dst)
        print(f"Copied: {src} -> {dst}")
    else:
        with open(dst, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n#EXTINF:-1," + fallback_name + "\nhttp://example.com/stream\n")
        print(f"Fallback created: {dst} (source not found: {src})")

if __name__ == "__main__":
    safe_copy(SRC_BLINK, DST_BLINK, "Blink Fallback")
    safe_copy(SRC_FULL,  DST_FULL,  "Full Fallback")
    print("Done: public/blink.m3u & public/full.m3u")
