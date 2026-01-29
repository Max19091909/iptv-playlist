#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автопубликация плейлистов для GitHub Pages.

Берём уже готовые объединённые файлы из корня репозитория:
- UA_RU_BLINK.m3u  → публикуем как public/blink.m3u (с фильтром под Blink Player)
- UA_RU_FULL.m3u   → публикуем как public/full.m3u (без изменений)

Фильтр для blink.m3u:
- исключаем любые URL, оканчивающиеся на .mpd (DASH)
- исключаем любые URL, содержащие /iframe/ (непрямые потоки)

Если исходника нет — создаём безопасную заглушку, чтобы workflow не падал.
"""

import os
import shutil

# Путь к корню репозитория (подняться из scripts/)
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(REPO_ROOT)

OUT_DIR = os.path.join(REPO_ROOT, "public")
os.makedirs(OUT_DIR, exist_ok=True)

# Исходники (лежать должны в КОРНЕ репо)
SRC_BLINK = os.path.join(REPO_ROOT, "UA_RU_BLINK.m3u")
SRC_FULL  = os.path.join(REPO_ROOT, "UA_RU_FULL.m3u")

# Назначение
DST_BLINK = os.path.join(OUT_DIR, "blink.m3u")
DST_FULL  = os.path.join(OUT_DIR, "full.m3u")


def write_fallback(dst_path: str, name: str) -> None:
    """Записывает минимальную заглушку в файл dst_path."""
    content = "#EXTM3U\n#EXTINF:-1,{name}\nhttp://example.com/stream\n".format(name=name)
    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Fallback created: {dst_path}")


def copy_full() -> None:
    """Копирует UA_RU_FULL.m3u в public/full.m3u как есть, либо пишет заглушку."""
    if os.path.isfile(SRC_FULL):
        shutil.copyfile(SRC_FULL, DST_FULL)
        print(f"Copied: {SRC_FULL} -> {DST_FULL}")
    else:
        write_fallback(DST_FULL, "Full Fallback")


def filter_and_copy_blink() -> None:
    """
    Читает UA_RU_BLINK.m3u, фильтрует неподдерживаемые для Blink потоки
    (.mpd и /iframe/) и записывает в public/blink.m3u. Если исходник отсутствует,
    пишет заглушку.
    """
    if not os.path.isfile(SRC_BLINK):
        write_fallback(DST_BLINK, "Blink Fallback")
        return

    with open(SRC_BLINK, "r", encoding="utf-8", errors="ignore") as src:
        lines = src.readlines()

    filtered = []
    i = 0
    # Простой парсер: #EXTINF строка + следующий URL (или пропуск)
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("#EXTINF"):
            extinf = line.rstrip("\n")
            # По умолчанию предполагаем, что следующая строка — URL
            url = ""
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith("#"):
                    url = next_line

            # Применяем фильтр под Blink
            u = url.lower()
            drop = False
            if u.endswith(".mpd"):
                drop = True
            if "/iframe/" in u:
                drop = True

            if not drop and url:
                filtered.append(extinf + "\n")
                filtered.append(url + "\n")
            # Переходим через пару строк
            i += 2
        else:
            # Дополнительно пропускаем несистемные строки (кроме #EXTM3U)
            if line.strip().startswith("#EXTM3U") and not filtered:
                filtered.append("#EXTM3U\n")
            i += 1

    # Если после фильтра нет ни одного канала — добавим минимальную заглушку
    if len(filtered) <= 1:  # либо пусто, либо только #EXTM3U
        print("Blink filter resulted in empty list. Writing fallback.")
        write_fallback(DST_BLINK, "Blink Safe Fallback")
        return

    with open(DST_BLINK, "w", encoding="utf-8") as dst:
        dst.writelines(filtered)

    print(f"Filtered & wrote: {DST_BLINK}")
    print(f"Total lines: {len(filtered)}")


def main() -> None:
    # Гарантируем наличие папки public/
    os.makedirs(OUT_DIR, exist_ok=True)

    # Выполняем публикацию
    filter_and_copy_blink()
    copy_full()

    # Покажем содержимое public/
    print("List public/:")
    for name in os.listdir(OUT_DIR):
        path = os.path.join(OUT_DIR, name)
        print(f"- {name} ({os.path.getsize(path)} bytes)")


if __name__ == "__main__":
    main()
