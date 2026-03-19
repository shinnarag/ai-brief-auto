"""
AI Creative Weekly Brief — 자동 생성 스크립트 v2
- Sound Republica 스타일 다크 디자인
- 개별 브리프 페이지(brief_YYYY-MM-DD.html) 생성
- briefs.json 누적 업데이트
- index.html (메인 아카이브 + 키워드 클라우드) 재생성
"""

import os, json, re
from datetime import datetime, timedelta
import anthropic
from tavily import TavilyClient

anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
tavily_client    = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

today    = datetime.utcnow()
weekday  = today.weekday()
days_back, edition = (4,"월요일") if weekday == 0 else (3,"목요일")
since_date = (today - timedelta(days=days_back)).strftime("%Y-%m-%d")
today_str  = today.strftime("%Y-%m-%d")
print(f"[INFO] {edition} 판 | 수집: {since_date} ~ {today_str}")

month_str = today.strftime('%B %Y')
SEARCH_QUERIES = {
    "Video AI": [
        f"AI video generation model release update {month_str}",
        f"text to video AI tool news {month_str}",
    ],
    "Music AI": [
        f"AI music generation tool model release {month_str}",
        f"generative AI music production update {month_str}",
    ],
    "Design AI": [
        f"AI design tool Adobe Figma Canva release {month_str}",
        f"generative AI image design model update {month_str}",
    ],
    "AI Content Marketing": [
        f"AI content marketing strategy issue {month_str}",
        f"AI generated content copyright brand regulation {month_str}",
    ],
}

def search_section(queries):
    results = []
    for q in queries:
        try:
            r = tavily_client.search(q, search_depth="advanced", max_results=6, include_published_date=True)
            for item in r.get("results", []):
                results.append({
                    "title":          item.get("title",""),
                    "url":            item.get("url",""),
                    "content":        item.get("content","")[:900],
                    "published_date": item.get("published_date",""),
                })
        except Exception as e:
            print(f"  [WARN] {q[:40]}: {e}")
    return results

print("[INFO] 웹 검색 중...")
search_data = {}
for sec, qs in SEARCH_QUERIES.items():
    search_data[sec] = search_section(qs)
    print(f"  v {sec}: {len(search_data[sec])}건")

SHARED_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Noto+Sans+KR:wght@300;400;500;700&family=Space+Mono:wght@400;700&family=Noto+Serif+KR:wght@400;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0a0a0a;--surface:#111;--surface2:#1a1a1a;--border:#2a2a2a;
  --text:#e8e4dc;--muted:#6b6860;--accent:#e8c547;--accent2:#4a9eff;
  --tag-video:#4a9eff;--tag-music:#b47dff;--tag-design:#4ecf8a;--tag-content:#ff6b6b;
}
html{background:var(--bg);color:var(--text);font-family:'Noto Sans KR',sans-serif;font-size:15px;line-height:1.7}
a{color:inherit;text-decoration:none}
::selection{background:var(--accent);color:#000}
nav{
  position:sticky;top:0;z-index:100;
  display:flex;justify-content:space-between;align-items:center;
  padding:.9rem 2rem;
  background:rgba(10,10,10,.92);
  backdrop-filter:blur(12px);
  border-bottom:1px solid var(--border);
}
.nav-logo{font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:.12em;color:var(--accent)}
.nav-links{display:flex;gap:1.5rem;font-family:'Space Mono',monospace;font-size:.68rem;letter-spacing:.1em;color:var(--muted)}
.nav-links a:hover{color:var(--text)}
.hero{padding:5rem 2rem 3rem;border-bottom:1px solid var(--border);max-width:1100px;margin:0 auto}
.hero-eyebrow{font-family:'Space Mono',monospace;font-size:.65rem;letter-spacing:.22em;text-transform:uppercase;color:var(--accent);margin-bottom:1rem}
.hero-title{font-family:'Bebas Neue',sans-serif;font-size:clamp(3.5rem,10vw,7rem);letter-spacing:.04em;line-height:.95;color:var(--text)}
.hero-title span{color:var(--accent)}
.hero-meta{display:flex;gap:2rem;margin-top:1.5rem;font-family:'Space Mono',monospace;font-size:.68rem;color:var(--muted);letter-spacing:.06em}
.section-head{display:flex;align-items:center;gap:1rem;padding:.5rem 0;border-top:1px solid var(--border);margin-bottom:1.2rem}
.section-num{font-family:'Space Mono',monospace;font-size:.6rem;color:var(--muted);letter-spacing:.14em}
.section-tag{font-family:'Space Mono',monospace;font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;padding:.22rem .65rem;border-radius:2px;color:#000;font-weight:700}
.tag-video{background:var(--tag-video)}.tag-music{background:var(--tag-music)}.tag-design{background:var(--tag-design)}.tag-content{background:var(--tag-content)}
.section-title{font-family:'Noto Serif KR',serif;font-size:1.15rem;font-weight:700;color:var(--text)}
.item{background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--border);border-radius:3px;padding:1.2rem 1.5rem;margin-bottom:.9rem;transition:border-color .2s,background .2s}
.item:hover{border-left-color:var(--accent);background:var(--surface2)}
.item-meta{display:flex;flex-wrap:wrap;gap:.5rem 1rem;align-items:center;margin-bottom:.5rem}
.item-title{font-family:'Noto Serif KR',serif;font-size:1rem;font-weight:700;line-height:1.4;color:var(--text)}
.item-date{font-family:'Space Mono',monospace;font-size:.62rem;color:var(--muted);background:var(--surface2);border:1px solid var(--border);padding:.12rem .4rem;border-radius:2px}
.item-source{font-family:'Space Mono',monospace;font-size:.62rem;color:var(--accent2);font-weight:700;text-transform:uppercase;letter-spacing:.06em}
.item-summary{font-size:.88rem;line-height:1.8;color:#c0bbb2;margin:.6rem 0}
.item-implication{border-left:3px solid var(--accent);padding:.55rem 1rem;margin:.7rem 0 .4rem;background:rgba(232,197,71,.05);font-size:.84rem;line-height:1.7;color:#d4cfc7}
.item-implication strong{display:block;margin-bottom:.2rem;font-family:'Space Mono',monospace;font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:var(--accent)}
.item-link{display:inline-block;margin-top:.4rem;font-family:'Space Mono',monospace;font-size:.63rem;color:var(--accent2);border-bottom:1px dashed var(--accent2);word-break:break-all}
.item-link:hover{color:var(--accent);border-color:var(--accent)}
.keyword-cloud{display:flex;flex-wrap:wrap;align-items:center;gap:.6rem 1.2rem;padding:1.8rem 0}
.kw{font-family:'Bebas Neue',sans-serif;letter-spacing:.06em;transition:color .2s;cursor:default}
.kw:hover{color:var(--accent)}
.kw-1{font-size:2.4rem;color:var(--text)}.kw-2{font-size:1.8rem;color:#bbb5ac}.kw-3{font-size:1.35rem;color:#8a857e}.kw-4{font-size:1.05rem;color:#6b6860}.kw-5{font-size:.85rem;color:#504e4a}
.archive-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1px;background:var(--border)}
.archive-card{background:var(--bg);padding:1.8rem;transition:background .15s}
.archive-card:hover{background:var(--surface)}
.archive-card-date{font-family:'Space Mono',monospace;font-size:.62rem;color:var(--accent);letter-spacing:.1em;margin-bottom:.5rem}
.archive-card-title{font-family:'Bebas Neue',sans-serif;font-size:1.3rem;letter-spacing:.06em;color:var(--text);margin-bottom:.8rem;line-height:1.1}
.archive-card-kws{display:flex;flex-wrap:wrap;gap:.3rem;margin-bottom:1rem}
.archive-card-kw{font-family:'Space Mono',monospace;font-size:.58rem;color:var(--muted);border:1px solid var(--border);padding:.1rem .4rem;border-radius:2px}
.archive-card-link{font-family:'Space Mono',monospace;font-size:.63rem;color:var(--accent2);border-bottom:1px dashed var(--accent2)}
footer{text-align:center;padding:3rem 1rem;border-top:1px solid var(--border);margin-top:4rem;font-family:'Space Mono',monospace;font-size:.62rem;color:var(--muted);letter-spacing:.08em;line-height:2.2}
hr.div{border:none;border-top:1px solid var(--border);margin:2.5rem 0 0}
.container{max-width:1100px;margin:0 auto;padding:0 2rem}
.section{margin-top:2.8rem}
.empty{color:var(--muted);font-size:.85rem;padding:1.2rem;border:1px dashed var(--border);text-align:center;font-family:'Space Mono',monospace}
@media(max-width:600px){.hero{padding:3rem 1rem 2rem}.container{padding:0 1rem}.hero-meta{flex-wrap:wrap;gap:.6rem}}
"""

BRIEF_SYSTEM = """당신은 AI 크리에이티브 산업 전문 리서처입니다.
반드시 아래 형식으로만 출력하세요:

===HTML_START===
(완전한 HTML 문서)
===HTML_END===
===KEYWORDS_START===
[{"word":"키워드","score":5}, {"word":"키워드","score":4}, {"word":"키워드","score":3}, {"word":"키워드","score":2}, {"word":"키워드","score":1}]
===KEYWORDS_END===

HTML 외 설명 절대 금지."""

BRIEF_USER = f"""아래 검색 결과로 AI 크리에이티브 위클리 브리프 HTML을 작성하세요.

오늘: {today_str} / {edition} 판 / 수집기간: {since_date}~{today_str}

콘텐츠 규칙:
- 섹션 4개: Video AI / Music AI / Design AI / AI 콘텐츠·마케팅 이슈
- 각 섹션 최대 5건
- 수집 기간({since_date}~{today_str}) 내 발행 이슈만. 과거 이슈 절대 포함 금지
- 최신 AI 도구/모델 업데이트 우선 포함 (영상 생성, 디자인 AI, 음악 AI 등)
- 콘텐츠/마케팅 팀 실무자 대상
- 각 아이템: 제목(한국어)/발행일/출처/요약2~3문장/실무시사점/원문링크
- 이슈 없는 섹션: "발견된 이슈없음"

HTML 디자인:
<style> 안에 아래 CSS 전체 삽입:
{SHARED_CSS}

구조:
<!DOCTYPE html><html lang="ko">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI 브리프 {today_str}</title><style>[CSS]</style></head>
<body>
<nav><span class="nav-logo">AI BRIEF</span><div class="nav-links"><a href="index.html">← 아카이브</a></div></nav>
<div class="hero">
  <p class="hero-eyebrow">AI CREATIVE BRIEF · {edition.upper()} EDITION</p>
  <h1 class="hero-title">AI<br><span>크리에이티브</span><br>브리프</h1>
  <div class="hero-meta"><span>발행 {today_str}</span><span>수집 {since_date}~{today_str}</span><span>{edition} 판</span></div>
</div>
<div class="container">
[섹션 4개: section-head + item cards + hr.div]
</div>
<footer>AI CREATIVE BRIEF · {today_str}</footer>
</body></html>

섹션 클래스: tag-video / tag-music / tag-design / tag-content
번호: 01~04

키워드: 브리프 전체 핵심 키워드 5개, score 5(최고)~1(낮음). 한국어 또는 영문 고유명사.

검색결과:
{json.dumps(search_data, ensure_ascii=False, indent=2)}
"""

print("[INFO] Claude API 호출 중...")
msg = anthropic_client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=9000,
    system=BRIEF_SYSTEM,
    messages=[{"role":"user","content":BRIEF_USER}],
)
raw = msg.content[0].text
print(f"[INFO] 응답 수신 ({len(raw):,} chars)")

def extract_between(text, s, e):
    try: return text.split(s)[1].split(e)[0].strip()
    except: return ""

html_content = extract_between(raw, "===HTML_START===", "===HTML_END===")
kw_str       = extract_between(raw, "===KEYWORDS_START===", "===KEYWORDS_END===")

if not html_content:
    for fence in ["```html","```"]:
        if fence in raw:
            html_content = raw.split(fence)[1].split("```")[0].strip(); break
    if not html_content: html_content = raw

try: keywords = json.loads(kw_str)
except:
    m = re.search(r'\[.*?\]', kw_str, re.DOTALL)
    try: keywords = json.loads(m.group()) if m else []
    except: keywords = []

if not keywords:
    keywords = [{"word":"AI","score":5},{"word":"영상생성","score":4},
                {"word":"음악AI","score":3},{"word":"디자인","score":2},{"word":"마케팅","score":1}]

print(f"[INFO] 키워드: {[k['word'] for k in keywords]}")

brief_filename = f"brief_{today_str}.html"
with open(brief_filename, "w", encoding="utf-8") as f:
    f.write(html_content)
print(f"[DONE] {brief_filename} 저장")

BRIEFS_JSON = "briefs.json"
try:
    with open(BRIEFS_JSON, "r", encoding="utf-8") as f: briefs = json.load(f)
except: briefs = []

briefs = [b for b in briefs if b.get("date") != today_str]
briefs.insert(0, {"date":today_str,"edition":edition,"filename":brief_filename,"keywords":keywords})
briefs = briefs[:20]

with open(BRIEFS_JSON, "w", encoding="utf-8") as f:
    json.dump(briefs, f, ensure_ascii=False, indent=2)
print(f"[DONE] briefs.json 업데이트 ({len(briefs)}개)")

def render_keyword_cloud(kws):
    items = sorted(kws, key=lambda x: x["score"], reverse=True)
    html = '<div class="keyword-cloud">'
    for kw in items:
        cls = f"kw kw-{6 - min(max(kw['score'],1),5)}"
        html += f'<span class="{cls}">{kw["word"]}</span>'
    return html + '</div>'

def render_archive_cards(briefs):
    if not briefs:
        return '<p style="color:var(--muted);padding:2rem;font-family:\'Space Mono\',monospace;font-size:.75rem">아직 발행된 브리프가 없습니다.</p>'
    html = '<div class="archive-grid">'
    for b in briefs:
        kws_html = "".join(f'<span class="archive-card-kw">{k["word"]}</span>' for k in b.get("keywords",[]))
        html += f'<div class="archive-card"><div class="archive-card-date">{b["date"]} · {b["edition"]} 판</div><div class="archive-card-title">AI 크리에이티브<br>브리프</div><div class="archive-card-kws">{kws_html}</div><a class="archive-card-link" href="{b["filename"]}">브리프 보기 →</a></div>'
    return html + '</div>'

latest_kws   = briefs[0]["keywords"] if briefs else []
latest_link  = briefs[0]["filename"] if briefs else "#"
latest_date  = briefs[0]["date"]     if briefs else today_str

INDEX_HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI 크리에이티브 브리프 — 아카이브</title>
<style>{SHARED_CSS}</style>
</head>
<body>
<nav>
  <span class="nav-logo">AI BRIEF</span>
  <div class="nav-links"><a href="{latest_link}">최신 브리프</a><span>아카이브</span></div>
</nav>
<div class="hero">
  <p class="hero-eyebrow">AI CREATIVE BRIEF · ARCHIVE</p>
  <h1 class="hero-title">AI<br><span>크리에이티브</span><br>브리프</h1>
  <div class="hero-meta">
    <span>매주 월·목 자동 발행</span>
    <span>Video / Music / Design / Content AI</span>
    <span>총 {len(briefs)}개 브리프</span>
  </div>
</div>
<div class="container">
  <div class="section">
    <div class="section-head">
      <span class="section-num">이번 호 /</span>
      <span class="section-tag tag-video">KEYWORDS</span>
      <span class="section-title">주요 키워드 — {latest_date}</span>
    </div>
    {render_keyword_cloud(latest_kws)}
    <div style="margin-top:1.2rem">
      <a href="{latest_link}" class="item-link" style="font-size:.75rem">→ 최신 브리프 전체 보기</a>
    </div>
  </div>
  <hr class="div">
  <div class="section">
    <div class="section-head">
      <span class="section-num">전체 /</span>
      <span class="section-tag tag-content">ARCHIVE</span>
      <span class="section-title">브리프 아카이브</span>
    </div>
    {render_archive_cards(briefs)}
  </div>
</div>
<footer>
  AI CREATIVE BRIEF · 매주 월·목 자동 발행<br>
  GitHub Actions + Claude API + Tavily<br>
  <span style="font-size:.55rem;opacity:.5">Generated {today_str}</span>
</footer>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(INDEX_HTML)
print("[DONE] index.html 재생성")
print(f"[DONE] 토큰: input={msg.usage.input_tokens}, output={msg.usage.output_tokens}")
