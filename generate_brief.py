"""
AI Creative Weekly Brief 자동 생성 스크립트
- 실행 요일(월/목)에 따라 수집 기간 자동 계산
- Tavily로 웹 검색 → Claude API로 한국어 브리프 생성 → index.html 저장
"""

import os
import json
from datetime import datetime, timedelta
import anthropic
from tavily import TavilyClient

# ── API 클라이언트 초기화 ──────────────────────────────────
anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# ── 실행 요일 및 수집 기간 계산 ───────────────────────────
today = datetime.utcnow()
weekday = today.weekday()  # 0=월, 3=목

if weekday == 0:   # 월요일: 직전 4일
    days_back = 4
    edition = "월요일"
else:              # 목요일: 직전 3일
    days_back = 3
    edition = "목요일"

since_date = (today - timedelta(days=days_back)).strftime("%Y-%m-%d")
today_str = today.strftime("%Y-%m-%d")

print(f"[INFO] {edition} 판 실행 | 수집 기간: {since_date} ~ {today_str}")

# ── 검색 쿼리 정의 ────────────────────────────────────────
SEARCH_QUERIES = {
    "Video AI": [
        f"video AI generation tools news {today.strftime('%B %Y')}",
        f"AI video model release update {today.strftime('%B %Y')}",
    ],
    "Music AI": [
        f"music AI generation tool release {today.strftime('%B %Y')}",
        f"AI music model update news {today.strftime('%B %Y')}",
    ],
    "Design AI": [
        f"design AI tools Adobe Figma Canva update {today.strftime('%B %Y')}",
        f"generative AI design product release {today.strftime('%B %Y')}",
    ],
    "AI Content Marketing": [
        f"AI content marketing copyright regulation {today.strftime('%B %Y')}",
        f"AI generated content brand marketing issues {today.strftime('%B %Y')}",
    ],
}

# ── 웹 검색 실행 ──────────────────────────────────────────
def search_section(section_name, queries):
    results = []
    for query in queries:
        try:
            response = tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_published_date=True,
            )
            for r in response.get("results", []):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", "")[:800],
                    "published_date": r.get("published_date", ""),
                })
        except Exception as e:
            print(f"[WARN] 검색 실패 ({query}): {e}")
    return results

print("[INFO] 웹 검색 시작...")
search_data = {}
for section, queries in SEARCH_QUERIES.items():
    search_data[section] = search_section(section, queries)
    print(f"  ✓ {section}: {len(search_data[section])}건 수집")

# ── Claude에게 전달할 프롬프트 구성 ──────────────────────
search_json = json.dumps(search_data, ensure_ascii=False, indent=2)

SYSTEM_PROMPT = """당신은 AI 크리에이티브 산업 전문 리서처입니다.
제공된 웹 검색 결과를 바탕으로 한국어 AI 브리프 리포트를 작성합니다.
출력은 반드시 완전한 HTML 문서(<!DOCTYPE html>부터 </html>까지)여야 합니다.
HTML 외 어떤 설명도 추가하지 마세요."""

USER_PROMPT = f"""아래 웹 검색 결과를 분석해 AI 크리에이티브 위클리 브리프를 작성하세요.

## 실행 정보
- 오늘 날짜: {today_str}
- 판 종류: {edition} 판
- 수집 기간: {since_date} ~ {today_str}

## 작성 규칙
1. 섹션: Video AI / Music AI / Design AI / AI 콘텐츠·마케팅 이슈 (4개 고정)
2. 각 섹션 최대 5건, 수집 기간 내 발행 이슈 우선 (기간 외는 '참고'로 표시)
3. 중복 보도 통합, 공식 발표·제품 업데이트·신뢰 미디어 우선
4. 각 아이템 포함 요소:
   - 제목 (한국어)
   - 발행일 (YYYY-MM-DD)
   - 출처
   - 2~3문장 요약 (한국어)
   - 실무 시사점 또는 '왜 지금 중요한가'
   - 원문 링크
5. 이슈가 없는 섹션은 "발견된 이슈없음"으로 표시
6. AI 도구·모델 업데이트는 명시적으로 포함

## 검색 결과
{search_json}

## HTML 출력 형식
아래 디자인 스펙을 정확히 따르세요:

```html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI 위클리 브리프 — {today_str} ({edition} 판)</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;400;600;700&family=Noto+Sans+KR:wght@300;400;500;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #0f0e0d; --paper: #f5f0e8; --accent: #c8392b; --accent2: #1a5276;
    --muted: #7a7265; --rule: #d4c9b8; --card: #fff9f2;
    --tag-video: #1a5276; --tag-music: #7d3c98; --tag-design: #117a65; --tag-content: #c8392b;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--paper); color: var(--ink); font-family: 'Noto Sans KR', sans-serif; font-size: 15px; line-height: 1.7; }}
  .masthead {{ border-bottom: 3px double var(--ink); padding: 2rem 2rem 1rem; text-align: center; }}
  .masthead::before {{ content: ''; display: block; height: 4px; background: repeating-linear-gradient(90deg, var(--accent) 0 30px, transparent 30px 34px); margin-bottom: 1.5rem; }}
  .edition-label {{ font-family: 'Space Mono', monospace; font-size: 0.68rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--muted); margin-bottom: 0.6rem; }}
  .masthead h1 {{ font-family: 'Noto Serif KR', serif; font-size: clamp(1.8rem, 4vw, 3rem); font-weight: 700; }}
  .masthead h1 em {{ font-style: normal; color: var(--accent); }}
  .dateline {{ display: flex; justify-content: center; flex-wrap: wrap; gap: 0.5rem 1.4rem; margin-top: 0.8rem; font-family: 'Space Mono', monospace; font-size: 0.72rem; color: var(--muted); }}
  .container {{ max-width: 900px; margin: 0 auto; padding: 0 1.5rem; }}
  .section {{ margin-top: 3rem; }}
  .section-head {{ display: flex; align-items: center; gap: 0.8rem; border-top: 2px solid var(--ink); padding-top: 0.6rem; margin-bottom: 1.2rem; }}
  .section-num {{ font-family: 'Space Mono', monospace; font-size: 0.65rem; color: var(--muted); letter-spacing: 0.14em; }}
  .section-tag {{ font-family: 'Space Mono', monospace; font-size: 0.62rem; letter-spacing: 0.12em; text-transform: uppercase; color: #fff; padding: 0.2rem 0.6rem; border-radius: 2px; }}
  .tag-video {{ background: var(--tag-video); }} .tag-music {{ background: var(--tag-music); }}
  .tag-design {{ background: var(--tag-design); }} .tag-content {{ background: var(--tag-content); }}
  .section-title {{ font-family: 'Noto Serif KR', serif; font-size: 1.25rem; font-weight: 700; }}
  .item {{ background: var(--card); border: 1px solid var(--rule); border-left: 3px solid var(--rule); border-radius: 2px; padding: 1.2rem 1.4rem; margin-bottom: 1rem; }}
  .item:hover {{ border-left-color: var(--accent); }}
  .item-meta {{ display: flex; flex-wrap: wrap; gap: 0.5rem 1rem; align-items: center; margin-bottom: 0.5rem; }}
  .item-title {{ font-family: 'Noto Serif KR', serif; font-size: 1rem; font-weight: 600; line-height: 1.4; }}
  .item-date {{ font-family: 'Space Mono', monospace; font-size: 0.65rem; color: var(--muted); background: var(--rule); padding: 0.15rem 0.45rem; border-radius: 2px; }}
  .item-source {{ font-family: 'Space Mono', monospace; font-size: 0.65rem; color: var(--accent2); font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }}
  .item-summary {{ font-size: 0.9rem; line-height: 1.75; color: #2c2a28; margin: 0.6rem 0; }}
  .item-implication {{ background: linear-gradient(to right, #f0e6d8, transparent); border-left: 3px solid var(--accent); padding: 0.55rem 0.9rem; margin: 0.7rem 0 0.5rem; font-size: 0.875rem; line-height: 1.65; }}
  .item-implication strong {{ font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase; font-family: 'Space Mono', monospace; color: var(--accent); display: block; margin-bottom: 0.2rem; }}
  .item-link {{ display: inline-block; margin-top: 0.4rem; font-family: 'Space Mono', monospace; font-size: 0.66rem; color: var(--accent2); text-decoration: none; border-bottom: 1px dashed var(--accent2); word-break: break-all; }}
  .item-link:hover {{ color: var(--accent); border-color: var(--accent); }}
  .empty-section {{ color: var(--muted); font-size: 0.875rem; padding: 1rem; border: 1px dashed var(--rule); text-align: center; }}
  hr.section-divider {{ border: none; border-top: 1px solid var(--rule); margin: 2.8rem 0 0; }}
  footer {{ text-align: center; padding: 2.5rem 1rem; border-top: 2px double var(--ink); margin-top: 3.5rem; font-family: 'Space Mono', monospace; font-size: 0.65rem; color: var(--muted); letter-spacing: 0.08em; line-height: 2; }}
</style>
</head>
<body>
<div class="masthead">
  <p class="edition-label">📡 AI Weekly Brief · {edition} Edition · {today_str}</p>
  <h1>AI 크리에이티브 <em>위클리</em> 브리프</h1>
  <div class="dateline">
    <span>📅 발행일: {today_str} ({edition})</span>
    <span>📰 수집 기간: {since_date} ~ {today_str}</span>
  </div>
</div>
<div class="container">
  <!-- 여기에 4개 섹션을 순서대로 생성하세요 -->
  <!-- 각 섹션 구조:
  <div class="section">
    <div class="section-head">
      <span class="section-num">01 /</span>
      <span class="section-tag tag-video">Video AI</span>
      <span class="section-title">비디오 AI</span>
    </div>
    <div class="item">
      <div class="item-meta">
        <span class="item-date">YYYY-MM-DD</span>
        <span class="item-source">출처명</span>
      </div>
      <div class="item-title">제목</div>
      <p class="item-summary">요약 2~3문장</p>
      <div class="item-implication"><strong>실무 시사점</strong>내용</div>
      <a class="item-link" href="URL" target="_blank">→ 링크</a>
    </div>
  </div>
  <hr class="section-divider">
  -->
</div>
<footer>
  AI 크리에이티브 위클리 브리프 · {edition} 판 · 수집 기간 {since_date} ~ {today_str}<br>
  자동 생성 by GitHub Actions + Claude API · 원문 링크를 반드시 교차 확인하세요
</footer>
</body>
</html>
```

위 HTML 구조를 그대로 사용해 4개 섹션을 완성한 전체 HTML을 출력하세요.
"""

# ── Claude API 호출 ───────────────────────────────────────
print("[INFO] Claude API 호출 중...")
message = anthropic_client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=8000,
    system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": USER_PROMPT}],
)

html_content = message.content[0].text

# HTML 블록만 추출 (마크다운 펜스가 있을 경우 대비)
if "```html" in html_content:
    html_content = html_content.split("```html")[1].split("```")[0].strip()
elif "```" in html_content:
    html_content = html_content.split("```")[1].split("```")[0].strip()

# ── index.html 저장 ───────────────────────────────────────
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"[DONE] index.html 저장 완료 ({len(html_content):,} bytes)")
print(f"[DONE] 토큰 사용: input={message.usage.input_tokens}, output={message.usage.output_tokens}")
