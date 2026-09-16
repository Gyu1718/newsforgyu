#!/usr/bin/env python3
"""Generate the Pages /docs site using only the Python standard library."""
import argparse
from datetime import date
from html import escape
import json
import math
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE_PATH = "/newsforgyu/"
FONT_URL = "https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+KR:wght@400;500;600&display=swap"
WEEKDAYS = "월화수목금토일"


def text(value):
    return escape(str(value), quote=True)


def load_briefings():
    data = json.loads((ROOT / "data/briefings.json").read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("briefings"), list):
        raise ValueError("Expected version: 1 and a briefings array")
    seen = set()
    for item in data["briefings"]:
        for key in ("date", "market_date"):
            value = item[key]
            if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
                raise ValueError(f"{key} must use YYYY-MM-DD")
        if item["date"] in seen:
            raise ValueError(f"Duplicate briefing date: {item['date']}")
        seen.add(item["date"])
        if item["market_date"] > item["date"]:
            raise ValueError("market_date must not be after the briefing date")
        if item.get("status") not in {"summary", "published"}:
            raise ValueError("status must be summary or published")
        if not isinstance(item.get("summary"), str) or not item["summary"].strip():
            raise ValueError("Each briefing needs a summary")
        if type(item.get("unverified_count", 0)) is not int or item.get("unverified_count", 0) < 0:
            raise ValueError("unverified_count must be a nonnegative integer")
        for key in ("figures", "sections", "sources"):
            if not isinstance(item.get(key), list):
                raise ValueError(f"{key} must be an array")
        for figure in item["figures"]:
            if not isinstance(figure.get("label"), str) or not figure["label"].strip():
                raise ValueError("Each figure needs a label")
            value = figure.get("change_pct")
            if value is not None and (type(value) not in (int, float) or not math.isfinite(value)):
                raise ValueError("change_pct must be a finite number or null")
        for source in item["sources"]:
            parsed = urlparse(source["url"])
            if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
                raise ValueError("Sources must use HTTPS URLs without embedded credentials")
            if not isinstance(source.get("label"), str) or not source["label"].strip():
                raise ValueError("Each source needs a label")
        for section in item["sections"]:
            if not isinstance(section.get("title"), str) or not section["title"].strip():
                raise ValueError("Each section needs a title")
            paragraphs = section.get("paragraphs")
            if not isinstance(paragraphs, list) or not paragraphs or any(
                not isinstance(p, str) or not p.strip() for p in paragraphs
            ):
                raise ValueError("Each section needs nonempty text paragraphs")
        if item["status"] == "published" and (not item["sections"] or not item["sources"]):
            raise ValueError("Published briefings require body sections and source links")
    data["briefings"].sort(key=lambda item: item["date"], reverse=True)
    return data


def page(title, body, prefix="", script=False):
    script_tag = f'<script src="{prefix}assets/archive.js" defer></script>' if script else ""
    return f'''<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="description" content="국제 증시, 대륙별 국제사회, 국내, 캄보디아와 국제 개발협력 소식을 모으는 오전 8시 브리핑 아카이브입니다.">
  <meta name="color-scheme" content="light dark">
  <title>{text(title)} · 오전 8시 브리핑</title>
  <link rel="stylesheet" href="{text(FONT_URL)}">
  <link rel="stylesheet" href="{prefix}assets/site.css">
  {script_tag}
</head>
<body>
  <a class="skip" href="#main">본문으로 이동</a>
  <div class="wrap">
{body}
    <footer class="foot">확인되지 않은 값은 추정하지 않고 확인 상태를 표시합니다.<br>
    기관별 전망이 갈리는 항목은 출처와 함께 구분합니다. 새 브리핑은 등록 후 반영됩니다.</footer>
  </div>
</body>
</html>
'''


def figures_html(item):
    figures = []
    for figure in item["figures"]:
        value = figure.get("change_pct")
        css = "up" if value is not None and value > 0 else "down" if value is not None and value < 0 else ""
        display = "미확인" if value is None else f"{value:+.2f}%"
        figures.append(f'<span>{text(figure["label"])} <span class="{css}">{display}</span></span>')
    if item.get("unverified_count", 0):
        figures.append(f'<span>미확인 {item["unverified_count"]}건</span>')
    return '<div class="figs">' + "".join(figures) + "</div>" if figures else ""


def metadata(item):
    weekday = WEEKDAYS[date.fromisoformat(item["date"]).weekday()]
    status = "본문 미등록 · 요약만 보기" if item["status"] == "summary" else "본문 등록"
    return f'''<div class="d"><b><time datetime="{item['date']}">{item['date']}</time> {weekday}</b>
      <span>{item['market_date']} 미국장 마감 기준</span><span class="badge">{status}</span></div>'''


def archive(items):
    months = sorted({item["date"][:7] for item in items}, reverse=True)
    options = "".join(f'<option value="{month}">{month[:4]}년 {month[5:]}월</option>' for month in months)
    entries = []
    for item in items:
        entries.append(f'''<li class="item" data-month="{item['date'][:7]}">
        <a href="briefings/{item['date']}.html">
          {metadata(item)}
          <p class="sum">{text(item['summary'])}</p>
          {figures_html(item)}
          <span class="open">{'등록된 요약 확인' if item['status'] == 'summary' else '브리핑 읽기'} →</span>
        </a>
      </li>''')
    latest = f"최근 자료 {items[0]['date']}" if items else "첫 브리핑을 준비하고 있습니다"
    missing = '<p class="notice">본문 미등록 표시가 있는 브리핑은 기존 요약만 보관하고 있습니다. 해당 요약과 수치의 출처는 아직 확인되지 않았습니다.</p>' if any(i['status'] == 'summary' for i in items) else ''
    body = f'''    <header class="masthead">
      <div><p class="eyebrow">NEWS FOR GYU / ARCHIVE</p><h1>오전 8시 브리핑</h1></div>
      <div class="meta">아카이브 {len(items)}호<br>{latest}</div>
    </header>
    <main id="main" tabindex="-1">
      <p class="intro">국제 증시 · 대륙별 국제사회 · 국내 · 캄보디아 · 국제 개발협력.<br>날짜별로 쌓이는 소식을 한곳에서 읽습니다.</p>
      {missing}
      <form class="filters" id="filters" role="search" hidden>
        <div class="field"><label for="query">날짜·키워드 검색</label>
          <input id="query" type="search" placeholder="예: 2026-09-15, FOMC, 반도체" autocomplete="off" aria-controls="briefings"></div>
        <div class="field month"><label for="month">발행 월</label>
          <select id="month" aria-controls="briefings"><option value="">전체 기간</option>{options}</select></div>
        <button id="reset" type="button">검색 초기화</button>
      </form>
      <p class="count" id="count" role="status" aria-live="polite">{len(items)}개 브리핑 · 최신순</p>
      <ul class="list" id="briefings"{' hidden' if not items else ''}>{''.join(entries)}</ul>
      <p class="empty" id="empty"{'' if not items else ' hidden'}>검색 조건에 맞는 브리핑이 없습니다. 날짜나 키워드를 바꿔 주세요.</p>
    </main>'''
    return page("아카이브", body, script=True)


def briefing(item, older=None, newer=None):
    notice = '''<aside class="notice"><strong>본문 미등록 · 출처 확인 전</strong>
      <p>이 페이지에는 기존 아카이브에 등록되어 있던 요약만 보관하고 있습니다. 전체 본문과 근거 자료가 아직 등록되지 않아 아래 내용과 수치는 검증되지 않았습니다.</p></aside>''' if item["status"] == "summary" else ""
    sections = "".join(f'<section><h2>{text(s["title"])}</h2>' + "".join(f'<p>{text(p)}</p>' for p in s["paragraphs"]) + '</section>' for s in item["sections"])
    sources = '<h2>출처</h2><ul class="source-list">' + "".join(f'<li><a href="{text(s["url"])}" target="_blank" rel="noopener noreferrer">{text(s["label"])} ↗</a></li>' for s in item["sources"]) + '</ul>' if item["sources"] else '<h2>출처 확인 상태</h2><p>등록된 출처가 없습니다. 원문과 근거 자료를 확보한 후 보완할 수 있습니다.</p>'
    nav = '<a href="../index.html">전체 브리핑</a>'
    if older:
        nav = f'<a href="{older["date"]}.html">← {older["date"]}</a>' + nav
    if newer:
        nav += f'<a href="{newer["date"]}.html">{newer["date"]} →</a>'
    body = f'''    <a class="back" href="../index.html">← 아카이브로 돌아가기</a>
    <header class="masthead">
      <div><p class="eyebrow">오전 8시 브리핑</p><h1>{item['date']}</h1></div>
      <div class="meta">{item['market_date']} 미국장 마감 기준</div>
    </header>
    <main id="main" tabindex="-1">
      {notice}
      <article class="article">
        <h2>{'등록된 요약' if item['status'] == 'summary' else '오늘의 요약'}</h2>
        <p>{text(item['summary'])}</p>
        {figures_html(item)}
        {sections}
        {sources}
      </article>
      <nav class="article-nav" aria-label="브리핑 이동">{nav}</nav>
    </main>'''
    return page(item["date"], body, prefix="../")


def outputs(data):
    items = data["briefings"]
    files = {
        DOCS / "index.html": archive(items),
        DOCS / ".nojekyll": "",
        DOCS / "data/briefings.json": json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        DOCS / "404.html": page("페이지를 찾을 수 없습니다", f'''    <main id="main" tabindex="-1">
      <p class="eyebrow">404 / PAGE NOT FOUND</p><h1>페이지를 찾을 수 없습니다</h1>
      <p class="intro">주소가 바뀌었거나 아직 등록되지 않은 브리핑입니다.</p>
      <p><a href="{SITE_PATH}">브리핑 아카이브로 돌아가기 →</a></p></main>''', prefix=SITE_PATH),
    }
    for asset in ("site.css", "archive.js"):
        files[DOCS / "assets" / asset] = (ROOT / "assets" / asset).read_text(encoding="utf-8")
    for index, item in enumerate(items):
        files[DOCS / "briefings" / f"{item['date']}.html"] = briefing(
            item, items[index + 1] if index + 1 < len(items) else None,
            items[index - 1] if index else None,
        )
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check committed docs without writing")
    args = parser.parse_args()
    files = outputs(load_briefings())
    differences = []
    for path, content in files.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                differences.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    stale = sorted(set((DOCS / "briefings").glob("*.html")) - set(files))
    if stale:
        raise SystemExit("Unlisted briefing pages: " + ", ".join(str(p.relative_to(ROOT)) for p in stale))
    if differences:
        raise SystemExit("Run python3 scripts/build.py and commit updated files: " + ", ".join(differences))
    print(f"{'Checked' if args.check else 'Built'} {len(files)} site files.")


if __name__ == "__main__":
    main()
