"""
AI Creative Weekly Brief 자동 생성 스크립트
"""
import os, json
from datetime import datetime, timedelta
import anthropic
from tavily import TavilyClient

anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

today = datetime.utcnow()
weekday = today.weekday()
if weekday == 0:
    days_back, edition = 4, "월요일"
else:
    days_back, edition = 3, "목요일"

since_date = (today - timedelta(days=days_back)).strftime("%Y-%m-%d")
today_str = today.strftime("%Y-%m-%d")
print(f"[INFO] {edition} 판 | 수집 기간: {since_date} ~ {today_str}")

SEARCH_QUERIES = {
    "Video AI": [f"video AI generation tools news {today.strftime('%B %Y')}", f"AI video model release {today.strftime('%B %Y')}"],
    "Music AI": [f"music AI generation tool release {today.strftime('%B %Y')}", f"AI music model update {today.strftime('%B %Y')}"],
    "Design AI": [f"design AI tools Adobe Figma Canva update {today.strftime('%B %Y')}", f"generative AI design release {today.strftime('%B %Y')}"],
    "AI Content Marketing": [f"AI content marketing copyright regulation {today.strftime('%B %Y')}", f"AI generated content marketing issues {today.strftime('%B %Y')}"],
}

def search_section(queries):
    results = []
    for query in queries:
        try:
            resp = tavily_client.search(query=query, search_depth="advanced", max_results=5, include_published_date=True)
            for r in resp.get("results", []):
                results.append({"title": r.get("title",""), "url": r.get("url",""), "content": r.get("content","")[:800], "published_date": r.get("published_date","")})
        except Exception as e:
            print(f"[WARN] 검색 실패: {e}")
    return results

print("[INFO] 웹 검색 시작...")
search_data = {}
for section, queries in SEARCH_QUERIES.items():
    search_data[section] = search_section(queries)
    print(f"  ✓ {section}: {len(search_data[section])}건")

SYSTEM_PROMPT = "당신은 AI 크리에이티브 산업 전문 리서처입니다. 제공된 웹 검색 결과를 바탕으로 한국어 AI 브리프 리포트를 작성합니다. 출력은 반드시 완전한 HTML 문서(<!DOCTYPE html>부터 </html>까지)여야 합니다. HTML 외 어떤 설명도 추가하지 마세요."

USER_PROMPT = f"""아래 웹 검색 결과로 AI 크리에이티브 위클리 브리프 HTML을 작성하세요.

오늘: {today_str} / {edition} 판 / 수집기간: {since_date}~{today_str}

규칙:
- 섹션 4개 고정: Video AI / Music AI / Design AI / AI 콘텐츠·마케팅 이슈
- 각 섹션 최대 5건, 각 아이템에 제목·발행일·출처·2~3문장요약·실무시사점·링크 포함
- 이슈 없는 섹션은 "발견된 이슈없음" 표시

HTML 디자인 CSS 변수:
--ink:#0f0e0d; --paper:#f5f0e8; --accent:#c8392b; --accent2:#1a5276; --muted:#7a7265; --rule:#d4c9b8; --card:#fff9f2;
--tag-video:#1a5276; --tag-music:#7d3c98; --tag-design:#117a65; --tag-content:#c8392b;

폰트: Noto Serif KR(제목), Noto Sans KR(본문), Space Mono(메타)
구글폰트 링크 반드시 포함.
masthead에 빨간 줄무늬 상단바, 신문 레이아웃 스타일로 작성.
섹션마다 번호태그(01~04)와 색상 배지 포함.
각 아이템은 card 스타일, hover시 왼쪽 border accent 색상으로 변경.
실무시사점은 왼쪽 빨간 border + 연한 베이지 배경 처리.

검색결과:
{json.dumps(search_data, ensure_ascii=False, indent=2)}

완전한 HTML 문서만 출력하세요."""

print("[INFO] Claude API 호출 중...")
message = anthropic_client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=8000,
    system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": USER_PROMPT}],
)

html_content = message.content[0].text
if "```html" in html_content:
    html_content = html_content.split("```html")[1].split("```")[0].strip()
elif "```" in html_content:
    html_content = html_content.split("```")[1].split("```")[0].strip()

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"[DONE] index.html 저장 완료 ({len(html_content):,} bytes)")
print(f"[DONE] 토큰: input={message.usage.input_tokens}, output={message.usage.output_tokens}")
