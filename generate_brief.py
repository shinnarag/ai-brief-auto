"""
AI Creative Weekly Brief v3
- Claude가 JSON 데이터만 생성 (토큰 절약, 끊김 방지)
- Python이 HTML 완전 조립
- Sound Republica 다크 디자인
"""

import os, json, re
from datetime import datetime, timedelta
import anthropic
from tavily import TavilyClient

anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
tavily_client    = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

today      = datetime.utcnow()
weekday    = today.weekday()
days_back, edition = (4, "월요일") if weekday == 0 else (3, "목요일")
since_date = (today - timedelta(days=days_back)).strftime("%Y-%m-%d")
today_str  = today.strftime("%Y-%m-%d")
print(f"[INFO] {edition} 판 | 수집: {since_date} ~ {today_str}")

month_str = today.strftime("%B %Y")
QUERIES = {
    "video":   [f"AI video generation model release update {month_str}",
                f"text to video AI tool news {month_str}"],
    "music":   [f"AI music generation tool model release {month_str}",
                f"generative AI music production update {month_str}"],
    "design":  [f"AI design tool Adobe Figma Canva release {month_str}",
                f"generative AI image design model update {month_str}"],
    "content": [f"AI content marketing strategy issue {month_str}",
                f"AI generated content copyright brand regulation {month_str}"],
}

def search(queries):
    out = []
    for q in queries:
        try:
            r = tavily_client.search(q, search_depth="advanced",
                                     max_results=6, include_published_date=True)
            for item in r.get("results", []):
                out.append({
                    "title":   item.get("title", ""),
                    "url":     item.get("url", ""),
                    "content": item.get("content", "")[:700],
                    "date":    item.get("published_date", ""),
                })
        except Exception as e:
            print(f"  [WARN] {e}")
    return out

print("[INFO] 웹 검색 중...")
search_data = {}
for key, qs in QUERIES.items():
    search_data[key] = search(qs)
    print(f"  v {key}: {len(search_data[key])}건")

SYSTEM = """당신은 AI 크리에이티브 산업 전문 리서처입니다.
반드시 순수 JSON만 출력하세요. 마크다운 코드블록, 설명, 주석 절대 금지.
JSON 스키마:
{
  "keywords": [{"word": "string", "score": 1-5}],
  "sections": {
    "video":   [{"title":"","date":"YYYY-MM-DD","source":"","summary":"","implication":"","url":""}],
    "music":   [...],
    "design":  [...],
    "content": [...]
  }
}
keywords는 정확히 5개. sections 각 배열은 0~5개 아이템."""

USER = f"""검색 결과를 분석해 AI 크리에이티브 위클리 브리프 데이터를 JSON으로 출력하세요.

오늘: {today_str} / {edition} 판 / 수집기간: {since_date}~{today_str}

규칙:
- 수집 기간({since_date}~{today_str}) 내 발행된 이슈만. 과거 이슈 절대 금지
- 최신 AI 도구/모델 업데이트 우선 (영상 생성, 디자인 AI, 음악 AI 등)
- 콘텐츠/마케팅 팀 실무자 관점
- title(한국어)/date(YYYY-MM-DD)/source/summary(2~3문장 한국어)/implication(실무시사점)/url
- 이슈 없는 섹션은 빈 배열 []
- keywords: 핵심 키워드 5개, score 5=가장 중요

검색결과:
{json.dumps(search_data, ensure_ascii=False)}
"""

print("[INFO] Claude API 호출 중...")
msg = anthropic_client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4000,
    system=SYSTEM,
    messages=[{"role": "user", "content": USER}],
)
raw = msg.content[0].text.strip()
print(f"[INFO] 응답 수신 ({len(raw):,} chars)")

clean = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()
try:
    data = json.loads(clean)
except Exception as e:
    print(f"[ERROR] JSON 파싱 실패: {e}\n{raw[:300]}")
    raise

keywords = data.get("keywords", [])
sections = data.get("sections", {})
print(f"[INFO] 키워드: {[k['word'] for k in keywords]}")
for k, v in sections.items():
    print(f"  v {k}: {len(v)}건")

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Noto+Sans+KR:wght@300;400;500;700&family=Space+Mono:wght@400;700&family=Noto+Serif+KR:wght@400;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0a0a0a;--surface:#111;--surface2:#1a1a1a;--border:#2a2a2a;--text:#e8e4dc;--muted:#6b6860;--accent:#e8c547;--accent2:#4a9eff;--video:#4a9eff;--music:#b47dff;--design:#4ecf8a;--content:#ff6b6b}
html{background:var(--bg);color:var(--text);font-family:'Noto Sans KR',sans-serif;font-size:15px;line-height:1.7}
a{color:inherit;text-decoration:none}
::selection{background:var(--accent);color:#000}
nav{position:sticky;top:0;z-index:100;display:flex;justify-content:space-between;align-items:center;padding:.9rem 2rem;background:rgba(10,10,10,.92);backdrop-filter:blur(12px);border-bottom:1px solid var(--border)}
.nav-logo{font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:.12em;color:var(--accent)}
.nav-links{display:flex;gap:1.5rem;font-family:'Space Mono',monospace;font-size:.68rem;letter-spacing:.1em;color:var(--muted)}
.nav-links a:hover{color:var(--text)}
.hero{padding:5rem 2rem 3rem;border-bottom:1px solid var(--border);max-width:1100px;margin:0 auto}
.hero-eyebrow{font-family:'Space Mono',monospace;font-size:.65rem;letter-spacing:.22em;text-transform:uppercase;color:var(--accent);margin-bottom:1rem}
.hero-title{font-family:'Bebas Neue',sans-serif;font-size:clamp(3.5rem,10vw,7rem);letter-spacing:.04em;line-height:.95;color:var(--text)}
.hero-title span{color:var(--accent)}
.hero-meta{display:flex;flex-wrap:wrap;gap:1.5rem;margin-top:1.5rem;font-family:'Space Mono',monospace;font-size:.68rem;color:var(--muted);letter-spacing:.06em}
.container{max-width:1100px;margin:0 auto;padding:0 2rem}
.section{margin-top:2.8rem}
.section-head{display:flex;align-items:center;gap:1rem;padding:.5rem 0;border-top:1px solid var(--border);margin-bottom:1.2rem}
.section-num{font-family:'Space Mono',monospace;font-size:.6rem;color:var(--muted);letter-spacing:.14em}
.section-tag{font-family:'Space Mono',monospace;font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;padding:.22rem .65rem;border-radius:2px;color:#000;font-weight:700}
.t-video{background:var(--video)}.t-music{background:var(--music)}.t-design{background:var(--design)}.t-content{background:var(--content)}
.section-title{font-family:'Noto Serif KR',serif;font-size:1.15rem;font-weight:700;color:var(--text)}
.item{background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--border);border-radius:3px;padding:1.2rem 1.5rem;margin-bottom:.9rem;transition:border-color .2s,background .2s}
.item:hover{border-left-color:var(--accent);background:var(--surface2)}
.item-meta{display:flex;flex-wrap:wrap;gap:.5rem 1rem;align-items:center;margin-bottom:.6rem}
.item-title{font-family:'Noto Serif KR',serif;font-size:1rem;font-weight:700;line-height:1.4;color:var(--text)}
.item-date{font-family:'Space Mono',monospace;font-size:.62rem;color:var(--muted);background:var(--surface2);border:1px solid var(--border);padding:.12rem .4rem;border-radius:2px}
.item-source{font-family:'Space Mono',monospace;font-size:.62rem;color:var(--accent2);font-weight:700;text-transform:uppercase;letter-spacing:.06em}
.item-summary{font-size:.88rem;line-height:1.8;color:#c0bbb2;margin:.6rem 0}
.item-imp{border-left:3px solid var(--accent);padding:.55rem 1rem;margin:.7rem 0 .4rem;background:rgba(232,197,71,.05);font-size:.84rem;line-height:1.7;color:#d4cfc7}
.item-imp strong{display:block;margin-bottom:.2rem;font-family:'Space Mono',monospace;font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:var(--accent)}
.item-link{display:inline-block;margin-top:.4rem;font-family:'Space Mono',monospace;font-size:.63rem;color:var(--accent2);border-bottom:1px dashed var(--accent2);word-break:break-all}
.item-link:hover{color:var(--accent);border-color:var(--accent)}
.empty{color:var(--muted);font-size:.82rem;padding:1.2rem;border:1px dashed var(--border);text-align:center;font-family:'Space Mono',monospace;letter-spacing:.06em}
.kw-cloud{display:flex;flex-wrap:wrap;align-items:center;gap:.6rem 1.2rem;padding:1.8rem 0}
.kw{font-family:'Bebas Neue',sans-serif;letter-spacing:.06em;transition:color .2s;cursor:default}
.kw:hover{color:var(--accent)}
.kw-1{font-size:2.4rem;color:var(--text)}.kw-2{font-size:1.8rem;color:#bbb5ac}.kw-3{font-size:1.35rem;color:#8a857e}.kw-4{font-size:1.05rem;color:#6b6860}.kw-5{font-size:.85rem;color:#504e4a}
.archive-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1px;background:var(--border)}
.archive-card{background:var(--bg);padding:1.8rem;transition:background .15s}
.archive-card:hover{background:var(--surface)}
.ac-date{font-family:'Space Mono',monospace;font-size:.62rem;color:var(--accent);letter-spacing:.1em;margin-bottom:.5rem}
.ac-title{font-family:'Bebas Neue',sans-serif;font-size:1.3rem;letter-spacing:.06em;color:var(--text);margin-bottom:.8rem;line-height:1.1}
.ac-kws{display:flex;flex-wrap:wrap;gap:.3rem;margin-bottom:1rem}
.ac-kw{font-family:'Space Mono',monospace;font-size:.58rem;color:var(--muted);border:1px solid var(--border);padding:.1rem .4rem;border-radius:2px}
.ac-link{font-family:'Space Mono',monospace;font-size:.63rem;color:var(--accent2);border-bottom:1px dashed var(--accent2)}
hr.div{border:none;border-top:1px solid var(--border);margin:2.5rem 0 0}
footer{text-align:center;padding:3rem 1rem;border-top:1px solid var(--border);margin-top:4rem;font-family:'Space Mono',monospace;font-size:.62rem;color:var(--muted);letter-spacing:.08em;line-height:2.2}
@media(max-width:600px){.hero{padding:3rem 1rem 2rem}.container{padding:0 1rem}}
"""

SECTION_META = [
    ("video",   "01 /", "t-video",   "VIDEO AI",   "비디오 AI"),
    ("music",   "02 /", "t-music",   "MUSIC AI",   "뮤직 AI"),
    ("design",  "03 /", "t-design",  "DESIGN AI",  "디자인 AI"),
    ("content", "04 /", "t-content", "AI CONTENT", "AI 콘텐츠·마케팅"),
]

def build_items(items):
    if not items:
        return '<div class="empty">발견된 이슈없음</div>'
    html = ""
    for it in items:
        html += f"""<div class="item">
  <div class="item-meta">
    <span class="item-date">{it.get('date','')}</span>
    <span class="item-source">{it.get('source','')}</span>
  </div>
  <div class="item-title">{it.get('title','')}</div>
  <p class="item-summary">{it.get('summary','')}</p>
  <div class="item-imp"><strong>실무 시사점</strong>{it.get('implication','')}</div>
  <a class="item-link" href="{it.get('url','#')}" target="_blank">→ 원문 링크</a>
</div>"""
    return html

def build_sections(sec):
    html = ""
    for key, num, tag, en, ko in SECTION_META:
        html += f"""
<div class="section">
  <div class="section-head">
    <span class="section-num">{num}</span>
    <span class="section-tag {tag}">{en}</span>
    <span class="section-title">{ko}</span>
  </div>
  {build_items(sec.get(key, []))}
</div>
<hr class="div">"""
    return html

def build_kw_cloud(kws):
    kws_sorted = sorted(kws, key=lambda x: x["score"], reverse=True)
    html = '<div class="kw-cloud">'
    for kw in kws_sorted:
        rank = 6 - min(max(kw["score"], 1), 5)
        html += f'<span class="kw kw-{rank}">{kw["word"]}</span>'
    return html + '</div>'

def brief_html(sec, kws):
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI 크리에이티브 브리프 — {today_str}</title>
<style>{CSS}</style>
</head>
<body>
<nav>
  <span class="nav-logo">AI BRIEF</span>
  <div class="nav-links"><a href="index.html">← 아카이브</a></div>
</nav>
<div class="hero">
  <p class="hero-eyebrow">AI CREATIVE BRIEF · {edition.upper()} EDITION</p>
  <h1 class="hero-title">AI<br><span>크리에이티브</span><br>브리프</h1>
  <div class="hero-meta">
    <span>발행 {today_str}</span>
    <span>수집 {since_date} ~ {today_str}</span>
    <span>{edition} 판</span>
  </div>
</div>
<div class="container">
{build_sections(sec)}
</div>
<footer>
  AI CREATIVE BRIEF · 자동 생성 by GitHub Actions + Claude API<br>
  {today_str} · 원문 링크를 반드시 교차 확인하세요
</footer>
</body>
</html>"""

def index_html(briefs):
    total    = len(briefs)
    latest   = briefs[0] if briefs else {}
    lf       = latest.get("filename", "#")
    ld       = latest.get("date", today_str)
    lk       = latest.get("keywords", [])
    kw_html  = build_kw_cloud(lk) if lk else ""
    cards    = ""
    for b in briefs:
        kws_h = "".join(f'<span class="ac-kw">{k["word"]}</span>' for k in b.get("keywords",[]))
        cards += f'<div class="archive-card"><div class="ac-date">{b["date"]} · {b["edition"]} 판</div><div class="ac-title">AI 크리에이티브<br>브리프</div><div class="ac-kws">{kws_h}</div><a class="ac-link" href="{b["filename"]}">브리프 보기 →</a></div>'
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI 크리에이티브 브리프 — 아카이브</title>
<style>{CSS}</style>
</head>
<body>
<nav>
  <span class="nav-logo">AI BRIEF</span>
  <div class="nav-links"><a href="{lf}">최신 브리프</a><span>아카이브</span></div>
</nav>
<div class="hero">
  <p class="hero-eyebrow">AI CREATIVE BRIEF · ARCHIVE</p>
  <h1 class="hero-title">AI<br><span>크리에이티브</span><br>브리프</h1>
  <div class="hero-meta">
    <span>매주 월·목 자동 발행</span>
    <span>Video / Music / Design / Content AI</span>
    <span>총 {total}개 브리프</span>
  </div>
</div>
<div class="container">
  <div class="section">
    <div class="section-head">
      <span class="section-num">이번 호 /</span>
      <span class="section-tag t-video">KEYWORDS</span>
      <span class="section-title">주요 키워드 — {ld}</span>
    </div>
    {kw_html}
    <div style="margin-top:1.2rem"><a href="{lf}" class="item-link" style="font-size:.75rem">→ 최신 브리프 전체 보기</a></div>
  </div>
  <hr class="div">
  <div class="section">
    <div class="section-head">
      <span class="section-num">전체 /</span>
      <span class="section-tag t-content">ARCHIVE</span>
      <span class="section-title">브리프 아카이브</span>
    </div>
    <div class="archive-grid">{cards}</div>
  </div>
</div>
<footer>AI CREATIVE BRIEF · 매주 월·목 자동 발행<br>GitHub Actions + Claude API + Tavily<br><span style="font-size:.55rem;opacity:.5">Generated {today_str}</span></footer>
</body>
</html>"""

brief_fn = f"brief_{today_str}.html"
with open(brief_fn, "w", encoding="utf-8") as f:
    f.write(brief_html(sections, keywords))
print(f"[DONE] {brief_fn} 저장")

BRIEFS_JSON = "briefs.json"
try:
    with open(BRIEFS_JSON, "r", encoding="utf-8") as f: briefs = json.load(f)
except: briefs = []
briefs = [b for b in briefs if b.get("date") != today_str]
briefs.insert(0, {"date": today_str, "edition": edition, "filename": brief_fn, "keywords": keywords})
briefs = briefs[:20]
with open(BRIEFS_JSON, "w", encoding="utf-8") as f:
    json.dump(briefs, f, ensure_ascii=False, indent=2)
print(f"[DONE] briefs.json ({len(briefs)}개)")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(index_html(briefs))
print("[DONE] index.html")
print(f"[DONE] 토큰: input={msg.usage.input_tokens}, output={msg.usage.output_tokens}")
