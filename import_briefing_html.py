#!/usr/bin/env python3
"""브리핑 아티팩트 HTML 한 판을 data/briefings.json 항목으로 변환한다."""
import json, re, sys
from pathlib import Path
from html.parser import HTMLParser
from bs4 import BeautifulSoup

def convert(html_path, date, market_date=None):
    s = BeautifulSoup(Path(html_path).read_text(encoding='utf-8'), 'html.parser')
    date = date
    market_date = market_date or date
    # 요약: 1면 요점 첫 두 항목
    ledes = [li.get_text(' ', strip=True) for li in s.select('.lede li')]
    summary = ' '.join(ledes[:2])[:400]
    sections = []
    for sec in s.select('section[id]'):
        title = sec.select_one('.sec-head h2').get_text(strip=True)
        paras = []
        block = None
        for c in sec.find_all(recursive=False):
            cls = c.get('class') or []
            if c.name == 'h3':
                block = c.get_text(' ', strip=True)
                paras.append(f'[{block}]')
            elif 'items' in cls:
                for it in c.select('.item'):
                    t = it.select_one('.t').get_text(' ', strip=True)
                    b = it.select_one('.b').get_text(' ', strip=True)
                    src = it.select_one('.src')
                    tail = f' (출처: {src.get_text(" ", strip=True)})' if src else ''
                    paras.append(f'{t} — {b}{tail}')
            elif 'note' in cls:
                paras.append('확인 중: ' + c.get_text(' ', strip=True))
            elif 'tbl' in cls:
                for tr in c.select('tbody tr'):
                    cells = [td.get_text(' ', strip=True) for td in tr.find_all(['td', 'th'])]
                    paras.append(' · '.join(x for x in cells if x))
            elif 'tbl-note' in cls:
                paras.append(c.get_text(' ', strip=True))
        if paras:
            sections.append({'title': title, 'paragraphs': paras})
    # 출처
    seen, sources = set(), []
    for a in s.select('.src-grid a, .item .src a'):
        url = a.get('href', '')
        label = a.get_text(' ', strip=True)
        if not url.startswith('https://') or url in seen or not label:
            continue
        seen.add(url)
        sources.append({'label': label[:120], 'url': url})
    unverified = len(re.findall(r'미확인', s.get_text()))
    return {
        'date': date, 'market_date': market_date, 'status': 'published',
        'summary': summary, 'figures': [], 'unverified_count': unverified,
        'sections': sections, 'sources': sources,
    }

def main():
    html_path, date = sys.argv[1], sys.argv[2]
    data_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path('data/briefings.json')
    data = json.loads(data_path.read_text(encoding='utf-8'))
    entry = convert(html_path, date)
    data['briefings'] = [b for b in data['briefings'] if b['date'] != date] + [entry]
    data['briefings'].sort(key=lambda b: b['date'], reverse=True)
    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"{date}: 섹션 {len(entry['sections'])}개, 문단 {sum(len(x['paragraphs']) for x in entry['sections'])}개, 출처 {len(entry['sources'])}개")

if __name__ == '__main__':
    main()
