#!/usr/bin/env python3
"""Measure download speed using ten sequential HTTP requests."""

import argparse
import http.client
import time
import urllib.error
import urllib.parse
import urllib.request


REQUEST_COUNT = 10
CHUNK_SIZE = 64 * 1024


def download(url: str, timeout: float) -> tuple[int, float]:
    """Return body size in bytes and time until the entire body is read."""
    request = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
    started = time.perf_counter()
    size = 0
    with urllib.request.urlopen(request, timeout=timeout) as response:
        while chunk := response.read(CHUNK_SIZE):
            size += len(chunk)
        expected_size = response.headers.get("Content-Length")
        if expected_size is not None and size != int(expected_size):
            raise OSError("Сервер передал неполный ответ")
    return size, time.perf_counter() - started


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Скорость скачивания по результатам 10 последовательных запросов."
    )
    parser.add_argument("url", help="HTTP/HTTPS-адрес файла")
    args = parser.parse_args()
    parsed = urllib.parse.urlsplit(args.url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        parser.error("укажите полный HTTP/HTTPS-адрес")

    total_bytes = 0
    total_seconds = 0.0
    for number in range(1, REQUEST_COUNT + 1):
        try:
            size, seconds = download(args.url, timeout=60)
        except (OSError, ValueError, urllib.error.URLError, http.client.HTTPException) as error:
            parser.exit(1, f"Ошибка запроса {number}/{REQUEST_COUNT}: {error}\n")
        total_bytes += size
        total_seconds += seconds

    print(f"Выполнено запросов: {REQUEST_COUNT}")
    print(f"Среднее время запроса: {total_seconds / REQUEST_COUNT:.3f} с")
    print(f"Скачано: {total_bytes} байт ({total_bytes / 1024**2:.3f} MiB)")
    print(f"Скорость скачивания: {total_bytes / total_seconds / 1024**2:.3f} MiB/с")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
