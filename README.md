# 오전 8시 브리핑

국제 증시, 대륙별 국제사회, 국내, 캄보디아와 국제 개발협력 브리핑을 날짜별로 보관하는 정적 사이트입니다.

- 사이트: https://gyu1718.github.io/newsforgyu/
- 최신 브리핑 고정 주소: https://gyu1718.github.io/newsforgyu/latest.html
- RSS: https://gyu1718.github.io/newsforgyu/rss.xml
- Pages 설정: **Deploy from a branch → main → /docs**
- 실행 환경: Python 3.10 이상, 외부 패키지와 API 키 불필요

## 운영 방식

원고 작성과 사이트 생성은 분리합니다.

1. Claude 또는 작성자가 `data/briefings.json`만 수정합니다.
2. `main`에 반영되면 `Publish briefing site`가 사이트를 새로 생성하고 검사합니다.
3. 생성 결과가 달라졌을 때만 GitHub Actions가 `docs/`를 자동 커밋합니다.
4. GitHub Pages가 `main/docs`를 배포합니다.

따라서 평소에는 `docs/`의 HTML을 직접 수정하지 않습니다. `docs/`는 생성 결과물입니다.

`Validate site`는 PR과 `main` 변경에서 별도의 깨끗한 사이트를 만든 뒤 데이터 형식, 생성 결과, 내부 링크를 검사합니다. 생성 전 `docs/` 상태 때문에 정상적인 원고 커밋이 실패하지 않도록 구성되어 있습니다.

## 새 브리핑 등록

`data/briefings.json`의 `briefings` 배열에 새 항목을 추가합니다. 날짜는 `YYYY-MM-DD` 형식입니다.

```json
{
  "date": "2026-09-16",
  "market_date": "2026-09-15",
  "status": "published",
  "summary": "오늘 브리핑의 짧은 요약",
  "figures": [
    {"label": "S&P 500", "change_pct": 0.0}
  ],
  "unverified_count": 0,
  "sections": [
    {
      "title": "국제 증시",
      "paragraphs": ["확인한 기사와 지표를 바탕으로 작성한 본문"]
    }
  ],
  "sources": [
    {
      "label": "원문 제목 · 기관명",
      "url": "https://example.com/source"
    }
  ]
}
```

- 전체 본문과 출처가 있으면 `status`를 `published`로 둡니다.
- 요약만 임시 보관할 때는 `summary`로 둡니다.
- 확인하지 못한 등락률은 추정하지 말고 `null`로 기록합니다.
- `published` 항목은 최소 한 개 이상의 본문 섹션과 출처가 필요합니다.
- 출처 URL은 HTTPS만 허용합니다.

## 자동 생성되는 기능

- 날짜 역순 아카이브
- 날짜·키워드 검색과 발행 월 필터
- 날짜별 상세 페이지와 이전·다음 이동
- 최신 브리핑 고정 주소 `/latest.html`
- RSS 2.0 피드 `/rss.xml`
- 검색엔진용 `/sitemap.xml`과 `/robots.txt`
- 공개 구조화 데이터 `/data/briefings.json`
- 모바일 대응, 시스템 다크 모드, 키보드 이동, 인쇄 스타일
- 404 복귀 페이지

## 로컬 점검

```bash
rm -rf docs/briefings
python3 scripts/build.py
python3 scripts/site_extras.py
python3 scripts/build.py --check
python3 scripts/site_extras.py --check
python3 scripts/check_site.py
python3 -m http.server 8000 --directory docs
```

브라우저에서 `http://localhost:8000/`을 엽니다.

## 파일 구조

- `data/briefings.json`: 브리핑 원본 데이터
- `assets/`: 사이트 스타일과 아카이브 검색 기능
- `scripts/build.py`: 원본 검증, 아카이브와 상세 페이지 생성
- `scripts/site_extras.py`: latest, RSS, sitemap, robots 생성
- `scripts/check_site.py`: 내부 링크와 파일 누락 검사
- `.github/workflows/validate.yml`: 변경 사항 검증
- `.github/workflows/publish.yml`: 생성 결과 자동 반영
- `docs/`: GitHub Pages에 공개되는 생성 결과

뉴스 수집과 원고 작성 자체는 이 저장소의 자동화 범위 밖입니다. Claude가 작성한 원고가 `data/briefings.json`에 들어온 이후의 생성·검사·배포를 이 저장소가 담당합니다.
