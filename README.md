# 오전 8시 브리핑

국제 증시, 대륙별 국제사회, 국내, 캄보디아와 국제 개발협력 브리핑을 보관하는 정적 사이트입니다.

- 사이트: https://gyu1718.github.io/newsforgyu/
- Pages 설정: **Deploy from a branch → main → /docs**
- 필요한 도구: Python 3.10 이상. 추가 패키지, API 키, 서버는 필요하지 않습니다.

## 현재 운영 상태

배포 오류는 Pages가 지정한 `/docs` 폴더가 저장소에 없어서 발생했습니다. 현재 사이트 파일은 `docs/`에서 제공합니다. `.nojekyll`로 불필요한 Jekyll 변환을 건너뜁니다.

2026-09-15호는 기존 `index.html`에 있던 요약과 수치만 복구했습니다. 전체 본문과 출처는 저장소에 없었으므로 **본문 미등록·출처 확인 전**으로 표시합니다. 원래 자료는 최초 업로드 커밋 기록에도 남아 있습니다.

**매일 오전 8시에 뉴스를 수집하거나 작성하는 자동화는 아직 연결되어 있지 않습니다.** 브리핑 원고를 등록하면 Pages가 사이트를 배포합니다. 사이트 배포와 뉴스 수집·작성은 별개입니다.

## 새 브리핑 등록

1. `data/briefings.json`의 `briefings` 배열에 새 날짜의 항목을 추가합니다.
2. `summary`에 요약, `sections`에 본문, `sources`에 근거 링크를 기록합니다. 날짜는 `YYYY-MM-DD`를 사용합니다.
3. 전체 본문과 출처가 갖춰지면 `status`를 `published`로 지정합니다. 요약만 있다면 `summary`로 둡니다. 아직 확인하지 못한 등락률은 `null`로 기록합니다.
4. 다음 명령으로 HTML을 생성하고 검사합니다.

```bash
python3 scripts/build.py
python3 scripts/build.py --check
python3 scripts/check_site.py
```

5. 원본과 생성된 `docs/` 파일을 함께 커밋합니다. GitHub의 **Actions → pages build and deployment**에서 배포 성공을 확인합니다.

본문과 출처 구조는 다음과 같습니다. 실제 확인한 내용으로 채워 주세요.

```json
{
  "sections": [
    {"title": "국제 증시", "paragraphs": ["확인한 기사와 지표를 바탕으로 작성한 문단"]}
  ],
  "sources": [
    {"label": "원문 제목 · 기관명", "url": "https://example.com/source"}
  ]
}
```

이 예시는 구조 설명용이며 뉴스 데이터로 사용하지 않습니다. 항목의 다른 필드는 기존 파일을 참고합니다. HTML은 직접 수정하지 않습니다. 삭제한 날짜의 생성 파일이 남아 있으면 빌드가 알려 주므로 해당 파일을 확인해서 정리합니다.

## 기능

- 날짜 역순 아카이브, 날짜·키워드 검색, 발행 월 필터, 검색 초기화
- 상세 페이지, 이전·다음 브리핑 이동, 출처 링크
- 모바일 화면, 시스템 설정에 따른 다크 모드, 키보드 이동, 인쇄 스타일
- 자바스크립트 없이도 목록과 상세 페이지 열람 가능
- 없는 주소에서 아카이브로 돌아가는 404 페이지
- `docs/data/briefings.json`에 공개용 구조화 데이터 제공

## 로컬 확인

```bash
python3 -m http.server 8000 --directory docs
```

`http://localhost:8000/`에서 확인합니다. 404 페이지의 복귀 링크는 실제 프로젝트 경로 `/newsforgyu/`를 사용합니다.

## 파일 구조

- `data/briefings.json`: 브리핑 원본. 이 파일에서 내용을 관리합니다.
- `assets/`: 스타일과 검색 기능 원본.
- `scripts/build.py`: 원본 검증 및 사이트 생성. `--check`는 생성 결과가 최신인지 검사합니다.
- `scripts/check_site.py`: 배포할 HTML의 내부 링크와 파일 누락 검사.
- `docs/`: GitHub Pages에 공개하는 생성 결과.
- `index.html`: 저장소 루트를 열었을 때 `docs/`로 안내하는 진입점.

`Validate site` 워크플로는 변경할 때 생성 결과와 내부 링크를 검사합니다. 브랜치 보호 규칙으로 설정하지 않은 한, 이 검사는 Pages 배포를 차단하는 필수 조건은 아닙니다.
