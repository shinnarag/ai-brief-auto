"""
AI Creative Weekly Brief v8
- 카테고리 스티키 네비게이션 추가
- 스크롤 시 현재 섹션 하이라이트
"""

import os, json, re
from datetime import datetime, timedelta
from openai import OpenAI
import anthropic

openai_client    = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

today      = datetime.utcnow()
weekday    = today.weekday()
days_back, edition = (4, "월요일") if weekday == 0 else (3, "목요일")
since_date = (today - timedelta(days=days_back)).strftime("%Y-%m-%d")
today_str  = today.strftime("%Y-%m-%d")
print(f"[INFO] {edition} 판 | 수집: {since_date} ~ {today_str}")

month_str = today.strftime("%B %Y")

SEARCH_QUERIES = {
    "video": [
        f"video AI model update release announcement {month_str}",
        f"AI video generation new tool launch {month_str}",
    ],
    "music": [
        f"music AI model update release announcement {month_str}",
        f"AI music generation new tool launch {month_str}",
    ],
    "design": [
        f"image generation AI model update release {month_str}",
        f"AI design tool new feature announcement {month_str}",
    ],
    "content": [
        f"AI content marketing brand strategy {month_str}",
        f"AI generated content copyright regulation platform policy {month_str}",
    ],
    "trending": [
        f"YouTube Instagram Threads TikTok trending viral content this week",
        f"viral social media content trend short form video {month_str}",
    ],
}

def openai_search(query):
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-5.4",
            reasoning_effort="high",
            tools=[{"type": "web_search_preview"}],
            messages=[{
                "role": "user",
                "content": (
                    f"Search for the latest news about: {query}\n"
                    f"Return a JSON array of up to 6 results, each with: "
                    f"title, url, date (YYYY-MM-DD), source, summary (2-3 sentences in Korean). "
                    f"Only include items published after {since_date}. "
                    f"Return pure JSON array only, no markdown."
                )
            }],
        )
        raw = resp.choices[0].message.content or "[]"
        raw = re.sub(r"^```[a-z]*\n?", "", raw.strip()).rstrip("`").strip()
        return json.loads(raw)
    except Exception as e:
        print(f"  [WARN] {query[:40]}: {e}")
        return []

print("[INFO] OpenAI 웹 검색 중...")
search_data = {}
for key, queries in SEARCH_QUERIES.items():
    results = []
    for q in queries:
        results.extend(openai_search(q))
    seen, unique = set(), []
    for r in results:
        if r.get("url") not in seen:
            seen.add(r.get("url"))
            unique.append(r)
    search_data[key] = unique
    print(f"  ✓ {key}: {len(unique)}건")

SYSTEM = """당신은 AI 크리에이티브 산업 전문 리서처입니다.
반드시 순수 JSON만 출력하세요. 마크다운 코드블록·설명·주석 절대 금지.

JSON 스키마:
{
  "keywords": [{"word":"string","score":1-5}],
  "sections": {
    "video":    [{"title":"","date":"YYYY-MM-DD","source":"","badge":"","summary":"","implication":"","url":""}],
    "music":    [...],
    "design":   [...],
    "content":  [...],
    "trending": [{"title":"","date":"YYYY-MM-DD","platform":"","badge":"","summary":"","implication":"","url":""}]
  },
  "signals": ["string","string","string","string"]
}
keywords 5개. 각 섹션 0~5개. signals 3~4개."""

USER = f"""검색 결과를 분석해 AI 크리에이티브 위클리 브리프 JSON을 출력하세요.

오늘: {today_str} / {edition} 판 / 수집기간: {since_date}~{today_str}

섹션별 기준:
- video/music/design: 모델 출시·업데이트·신기능만. 리서치·통계·전망 기사 제외. 해당 없으면 []
- content: 마케팅 실무자 관련 AI 이슈. badge는 이슈 성격. implication 레이블은 "왜 지금 중요한가"
- trending: 플랫폼별 급상승 콘텐츠. platform 필드 필수. implication 레이블은 "트렌드 인사이트"
- signals: 이번 호 전체를 관통하는 핵심 시그널 3~4개

공통: title 한국어, summary 2~3문장 구체적 수치/모델명 포함, badge로 이슈 성격 분류

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
clean = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()
try:
    data = json.loads(clean)
except Exception as e:
    print(f"[ERROR] JSON 파싱 실패: {e}\n{raw[:300]}")
    raise

keywords = data.get("keywords", [])
sections = data.get("sections", {})
signals  = data.get("signals", [])
print(f"[INFO] 키워드: {[k['word'] for k in keywords]}")
for k, v in sections.items():
    print(f"  ✓ {k}: {len(v)}건")
print(f"[INFO] 토큰: in={msg.usage.input_tokens} out={msg.usage.output_tokens}")

# ── CSS ───────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Noto+Sans+KR:wght@300;400;500;700;900&family=Space+Mono:wght@400;700&family=Noto+Serif+KR:wght@400;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#f8f9fc;--surface:#ffffff;--surface2:#f0f3f8;--border:#dde3ee;
  --text:#0f1623;--text-sub:#374151;--muted:#6b7280;
  --accent:#1d4ed8;--accent-light:#eff6ff;--accent2:#0ea5e9;
  --video:#2563eb;--music:#7c3aed;--design:#059669;--content:#dc2626;--trending:#d97706;--signal:#d97706;
  --nav-bg:rgba(248,249,252,0.95);--imp-bg:#eff6ff;--imp-border:#1d4ed8;
  --kw1:#0f1623;--kw2:#1e3a6e;--kw3:#2563eb;--kw4:#6b7280;--kw5:#9ca3af;
}
[data-theme="dark"]{
  --bg:#080d16;--surface:#0f1623;--surface2:#161f30;--border:#1e2d45;
  --text:#e8edf5;--text-sub:#b8c4d4;--muted:#5a7090;
  --accent:#3b82f6;--accent-light:#0f1e35;--accent2:#38bdf8;
  --video:#3b82f6;--music:#a78bfa;--design:#34d399;--content:#f87171;--trending:#fbbf24;--signal:#fbbf24;
  --nav-bg:rgba(8,13,22,0.95);--imp-bg:#0f1e35;--imp-border:#3b82f6;
  --kw1:#e8edf5;--kw2:#93c5fd;--kw3:#3b82f6;--kw4:#5a7090;--kw5:#374151;
}
html{background:var(--bg);color:var(--text);font-family:'Noto Sans KR',sans-serif;font-size:15px;line-height:1.75;transition:background .25s,color .25s}
a{color:inherit;text-decoration:none}
::selection{background:var(--accent);color:#fff}

/* 메인 네비게이션 */
nav{position:sticky;top:0;z-index:100;display:flex;justify-content:space-between;align-items:center;padding:.85rem 2rem;background:var(--nav-bg);backdrop-filter:blur(14px);border-bottom:1.5px solid var(--border);transition:background .25s,border-color .25s}
.nav-logo{font-family:'Bebas Neue',sans-serif;font-size:1.45rem;letter-spacing:.14em;color:var(--accent)}
.nav-right{display:flex;align-items:center;gap:1.6rem}
.nav-links{display:flex;gap:1.4rem;font-family:'Space Mono',monospace;font-size:.68rem;letter-spacing:.08em;color:var(--muted);font-weight:700}
.nav-links a:hover{color:var(--text)}
.theme-toggle{display:flex;align-items:center;gap:.5rem;font-family:'Space Mono',monospace;font-size:.62rem;color:var(--muted);cursor:pointer;border:none;background:none;padding:0}
.toggle-track{width:36px;height:20px;background:var(--border);border-radius:10px;position:relative;transition:background .25s;border:1.5px solid var(--border)}
[data-theme="dark"] .toggle-track{background:var(--accent)}
.toggle-thumb{position:absolute;top:2px;left:2px;width:14px;height:14px;background:#fff;border-radius:50%;transition:transform .2s;box-shadow:0 1px 3px rgba(0,0,0,.2)}
[data-theme="dark"] .toggle-thumb{transform:translateX(16px)}

/* 카테고리 스티키 네비게이션 */
.cat-nav{position:sticky;top:56px;z-index:99;background:var(--nav-bg);backdrop-filter:blur(14px);border-bottom:1.5px solid var(--border);transition:background .25s}
.cat-nav-inner{max-width:1100px;margin:0 auto;padding:0 2rem;display:flex;overflow-x:auto;scrollbar-width:none}
.cat-nav-inner::-webkit-scrollbar{display:none}
.cat-btn{font-family:'Space Mono',monospace;font-size:.62rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:.75rem 1.1rem;color:var(--muted);border:none;border-bottom:2px solid transparent;background:none;cursor:pointer;white-space:nowrap;transition:color .15s,border-color .15s}
.cat-btn:hover{color:var(--text)}
.cat-btn.active{color:var(--accent);border-bottom-color:var(--accent)}

/* 히어로 */
.hero{padding:5rem 2rem 3.5rem;border-bottom:1.5px solid var(--border);max-width:1100px;margin:0 auto}
.hero-eyebrow{font-family:'Space Mono',monospace;font-size:.68rem;letter-spacing:.2em;text-transform:uppercase;color:var(--accent);font-weight:700;margin-bottom:1.1rem}
.hero-title{font-family:'Bebas Neue',sans-serif;font-size:clamp(3.8rem,10vw,7.5rem);letter-spacing:.04em;line-height:.92;color:var(--text)}
.hero-title span{color:var(--accent)}
.hero-meta{display:flex;flex-wrap:wrap;gap:1.4rem;margin-top:1.8rem;font-family:'Space Mono',monospace;font-size:.7rem;color:var(--muted);letter-spacing:.05em;font-weight:700}
.hero-meta span::before{content:'— ';opacity:.4}

/* 레이아웃 */
.container{max-width:1100px;margin:0 auto;padding:0 2rem}
.section{margin-top:3rem;scroll-margin-top:110px}
.section-head{display:flex;align-items:center;gap:1rem;padding:.6rem 0;border-top:2px solid var(--text);margin-bottom:1.4rem}
.section-num{font-family:'Space Mono',monospace;font-size:.62rem;color:var(--muted);letter-spacing:.14em;font-weight:700}
.section-tag{font-family:'Space Mono',monospace;font-size:.62rem;letter-spacing:.1em;text-transform:uppercase;padding:.25rem .7rem;border-radius:3px;color:#fff;font-weight:700}
.t-video{background:var(--video)}.t-music{background:var(--music)}.t-design{background:var(--design)}.t-content{background:var(--content)}.t-trending{background:var(--trending)}.t-signal{background:var(--signal)}
.section-title{font-family:'Noto Serif KR',serif;font-size:1.2rem;font-weight:700;color:var(--text)}

/* 아이템 카드 */
.item{background:var(--surface);border:1.5px solid var(--border);border-left:4px solid var(--border);border-radius:6px;padding:1.4rem 1.6rem;margin-bottom:1rem;transition:border-color .2s,box-shadow .2s}
.item:hover{border-left-color:var(--accent);box-shadow:0 4px 20px rgba(29,78,216,.08)}
[data-theme="dark"] .item:hover{box-shadow:0 4px 20px rgba(59,130,246,.12)}
.item-badge{display:inline-block;font-family:'Space Mono',monospace;font-size:.6rem;font-weight:700;letter-spacing:.06em;padding:.2rem .55rem;border-radius:3px;background:var(--accent-light);color:var(--accent);margin-bottom:.6rem}
.item-meta{display:flex;flex-wrap:wrap;gap:.5rem 1rem;align-items:center;margin-bottom:.65rem}
.item-title{font-family:'Noto Serif KR',serif;font-size:1.05rem;font-weight:700;line-height:1.45;color:var(--text)}
.item-date{font-family:'Space Mono',monospace;font-size:.65rem;font-weight:700;color:var(--muted);background:var(--surface2);border:1.5px solid var(--border);padding:.13rem .45rem;border-radius:3px}
.item-source{font-family:'Space Mono',monospace;font-size:.65rem;font-weight:700;color:var(--accent2);text-transform:uppercase;letter-spacing:.06em}
.item-platform{font-family:'Space Mono',monospace;font-size:.65rem;font-weight:700;color:var(--trending);text-transform:uppercase;letter-spacing:.06em;background:rgba(217,119,6,.1);padding:.13rem .45rem;border-radius:3px}
[data-theme="dark"] .item-platform{background:rgba(251,191,36,.1)}
.item-summary{font-size:.92rem;line-height:1.85;color:var(--text-sub);margin:.65rem 0}
.item-imp{border-left:4px solid var(--imp-border);padding:.65rem 1.1rem;margin:.8rem 0 .5rem;background:var(--imp-bg);border-radius:0 4px 4px 0;font-size:.88rem;line-height:1.75;color:var(--text-sub);font-weight:500}
.item-imp strong{display:block;margin-bottom:.25rem;font-family:'Space Mono',monospace;font-size:.62rem;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);font-weight:700}
.item-link{display:inline-flex;align-items:center;gap:.3rem;margin-top:.5rem;font-family:'Space Mono',monospace;font-size:.65rem;font-weight:700;color:var(--accent);border-bottom:1.5px solid transparent;transition:border-color .15s;word-break:break-all}
.item-link:hover{border-bottom-color:var(--accent)}
.empty{color:var(--muted);font-size:.82rem;font-weight:700;padding:1.4rem;border:1.5px dashed var(--border);text-align:center;border-radius:6px;font-family:'Space Mono',monospace;letter-spacing:.06em}

/* 키워드 클라우드 */
.kw-cloud{display:flex;flex-wrap:wrap;align-items:center;gap:.7rem 1.4rem;padding:2rem 0}
.kw{font-family:'Bebas Neue',sans-serif;letter-spacing:.06em;transition:opacity .2s;cursor:default}
.kw:hover{opacity:.7}
.kw-1{font-size:2.6rem;color:var(--kw1)}.kw-2{font-size:1.9rem;color:var(--kw2)}.kw-3{font-size:1.4rem;color:var(--kw3)}.kw-4{font-size:1.08rem;color:var(--kw4)}.kw-5{font-size:.88rem;color:var(--kw5)}

/* 시그널 */
.signals-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:1rem;margin-top:.5rem}
.signal-card{background:var(--surface);border:1.5px solid var(--border);border-left:4px solid var(--signal);border-radius:6px;padding:1.1rem 1.3rem;font-size:.9rem;line-height:1.75;color:var(--text-sub);font-weight:500}

/* 아카이브 */
.archive-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1.5px;background:var(--border);border:1.5px solid var(--border);border-radius:8px;overflow:hidden}
.archive-card{background:var(--surface);padding:1.8rem;transition:background .15s}
.archive-card:hover{background:var(--surface2)}
.ac-date{font-family:'Space Mono',monospace;font-size:.64rem;font-weight:700;color:var(--accent);letter-spacing:.1em;margin-bottom:.55rem}
.ac-title{font-family:'Bebas Neue',sans-serif;font-size:1.35rem;letter-spacing:.06em;color:var(--text);margin-bottom:.85rem;line-height:1.1}
.ac-kws{display:flex;flex-wrap:wrap;gap:.35rem;margin-bottom:1.1rem}
.ac-kw{font-family:'Space Mono',monospace;font-size:.6rem;font-weight:700;color:var(--muted);border:1.5px solid var(--border);padding:.12rem .45rem;border-radius:3px}
.ac-link{font-family:'Space Mono',monospace;font-size:.65rem;font-weight:700;color:var(--accent);border-bottom:1.5px solid var(--accent);display:inline-block}

hr.div{border:none;border-top:1.5px solid var(--border);margin:2.8rem 0 0}
footer{text-align:center;padding:3rem 1rem;border-top:1.5px solid var(--border);margin-top:4rem;font-family:'Space Mono',monospace;font-size:.64rem;font-weight:700;color:var(--muted);letter-spacing:.08em;line-height:2.4}
@media(max-width:600px){.hero{padding:3rem 1rem 2rem}.container{padding:0 1rem}.hero-meta{gap:.8rem}nav{padding:.8rem 1rem}.signals-grid{grid-template-columns:1fr}.cat-nav-inner{padding:0 1rem}}
"""

THEME_JS = """<script>
(function(){var s=localStorage.getItem('theme');if(s)document.documentElement.setAttribute('data-theme',s);})();
function toggleTheme(){
  var c=document.documentElement.getAttribute('data-theme');
  var n=c==='dark'?'light':'dark';
  document.documentElement.setAttribute('data-theme',n);
  localStorage.setItem('theme',n);
  var i=document.getElementById('toggle-icon');
  if(i)i.textContent=n==='dark'?'☀':'☽';
}
function goTo(id){
  var el=document.getElementById(id);
  if(el)el.scrollIntoView({behavior:'smooth',block:'start'});
}
window.addEventListener('scroll',function(){
  var ids=['s-video','s-music','s-design','s-content','s-trending','s-signals'];
  var current='';
  ids.forEach(function(id){
    var el=document.getElementById(id);
    if(el&&el.getBoundingClientRect().top<=120)current=id;
  });
  document.querySelectorAll('.cat-btn').forEach(function(b){
    b.classList.toggle('active',b.dataset.target===current);
  });
});
</script>"""

def nav_html(back_link, back_label, show_cat=False):
    cat = ""
    if show_cat:
        cats = [
            ("s-video",    "Video AI"),
            ("s-music",    "Music AI"),
            ("s-design",   "Design AI"),
            ("s-content",  "AI Content"),
            ("s-trending", "Trending"),
            ("s-signals",  "Signals"),
        ]
        btns = "".join(
            f'<button class="cat-btn" data-target="{sid}" onclick="goTo(\'{sid}\')">{label}</button>'
            for sid, label in cats
        )
        cat = f'<div class="cat-nav"><div class="cat-nav-inner">{btns}</div></div>'
    return f"""<nav>
  <span class="nav-logo">AI BRIEF</span>
  <div class="nav-right">
    <div class="nav-links"><a href="{back_link}">{back_label}</a></div>
    <button class="theme-toggle" onclick="toggleTheme()" aria-label="다크모드 전환">
      <span class="toggle-track"><span class="toggle-thumb"></span></span>
      <span id="toggle-icon">☽</span>
    </button>
  </div>
</nav>{cat}"""

SECTION_META = [
    ("video",    "01 /", "t-video",    "VIDEO AI",    "비디오 AI 모델",   "s-video"),
    ("music",    "02 /", "t-music",    "MUSIC AI",    "뮤직 AI 모델",     "s-music"),
    ("design",   "03 /", "t-design",   "DESIGN AI",   "디자인 AI 모델",   "s-design"),
    ("content",  "04 /", "t-content",  "AI CONTENT",  "AI 콘텐츠·마케팅", "s-content"),
    ("trending", "05 /", "t-trending", "TRENDING",    "급상승 콘텐츠",     "s-trending"),
]

def build_items(items, is_trending=False):
    if not items:
        return '<div class="empty">이번 기간 해당 업데이트 없음</div>'
    html = ""
    for it in items:
        badge     = it.get("badge", "")
        imp_label = "트렌드 인사이트" if is_trending else ("왜 지금 중요한가" if is_trending is False and "왜" in it.get("implication","") else "실무 시사점")
        source_badge = (
            f'<span class="item-platform">{it.get("platform","")}</span>'
            if is_trending else
            f'<span class="item-source">{it.get("source","")}</span>'
        )
        html += f"""<div class="item">
  {f'<div class="item-badge">{badge}</div>' if badge else ''}
  <div class="item-meta">
    <span class="item-date">{it.get('date','')}</span>
    {source_badge}
  </div>
  <div class="item-title">{it.get('title','')}</div>
  <p class="item-summary">{it.get('summary','')}</p>
  <div class="item-imp"><strong>{imp_label}</strong>{it.get('implication','')}</div>
  <a class="item-link" href="{it.get('url','#')}" target="_blank">→ 원문 링크</a>
</div>"""
    return html

def build_signals(signals):
    if not signals:
        return ""
    cards = "".join(f'<div class="signal-card">{s}</div>' for s in signals)
    return f"""<div class="section" id="s-signals" style="scroll-margin-top:110px">
  <div class="section-head">
    <span class="section-num">06 /</span>
    <span class="section-tag t-signal">SIGNALS</span>
    <span class="section-title">이번 주 핵심 시그널</span>
  </div>
  <div class="signals-grid">{cards}</div>
</div>"""

def build_sections(sec, signals):
    html = ""
    for key, num, tag, en, ko, sid in SECTION_META:
        html += f"""<div class="section" id="{sid}">
  <div class="section-head">
    <span class="section-num">{num}</span>
    <span class="section-tag {tag}">{en}</span>
    <span class="section-title">{ko}</span>
  </div>
  {build_items(sec.get(key,[]), key=="trending")}
</div>
<hr class="div">"""
    html += build_signals(signals)
    return html

def build_kw_cloud(kws):
    s = sorted(kws, key=lambda x: x["score"], reverse=True)
    html = '<div class="kw-cloud">'
    for kw in s:
        rank = 6 - min(max(kw["score"],1),5)
        html += f'<span class="kw kw-{rank}">{kw["word"]}</span>'
    return html + '</div>'

def brief_html(sec, kws, sigs):
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI 크리에이티브 브리프 — {today_str}</title>
{THEME_JS}
<style>{CSS}</style>
</head>
<body>
{nav_html("index.html", "← 아카이브", show_cat=True)}
<div class="hero">
  <p class="hero-eyebrow">AI CREATIVE BRIEF · {edition.upper()} EDITION</p>
  <h1 class="hero-title">AI<br><span>크리에이티브</span><br>브리프</h1>
  <div class="hero-meta">
    <span>발행 {today_str}</span>
    <span>수집 {since_date} ~ {today_str}</span>
    <span>{edition} 판</span>
  </div>
</div>
<div class="container">{build_sections(sec, sigs)}</div>
<footer>AI CREATIVE BRIEF · 자동 생성 by GitHub Actions + OpenAI + Claude<br>{today_str} · 원문 링크를 반드시 교차 확인하세요</footer>
</body>
</html>"""

def index_html(briefs):
    total=len(briefs); latest=briefs[0] if briefs else {}
    lf=latest.get("filename","#"); ld=latest.get("date",today_str); lk=latest.get("keywords",[])
    cards=""
    for b in briefs:
        kws_h="".join(f'<span class="ac-kw">{k["word"]}</span>' for k in b.get("keywords",[]))
        cards+=f'<div class="archive-card"><div class="ac-date">{b["date"]} · {b["edition"]} 판</div><div class="ac-title">AI 크리에이티브<br>브리프</div><div class="ac-kws">{kws_h}</div><a class="ac-link" href="{b["filename"]}">브리프 보기 →</a></div>'
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI 크리에이티브 브리프 — 아카이브</title>
{THEME_JS}
<style>{CSS}</style>
</head>
<body>
{nav_html(lf, "최신 브리프")}
<div class="hero">
  <p class="hero-eyebrow">AI CREATIVE BRIEF · ARCHIVE</p>
  <h1 class="hero-title">AI<br><span>크리에이티브</span><br>브리프</h1>
  <div class="hero-meta">
    <span>매주 월·목 자동 발행</span>
    <span>Video · Music · Design · Content · Trending</span>
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
    {build_kw_cloud(lk)}
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
<footer>AI CREATIVE BRIEF · 매주 월·목 자동 발행<br>GitHub Actions + OpenAI + Claude<br><span style="font-size:.6rem;opacity:.5">Generated {today_str}</span></footer>
</body>
</html>"""

# ── 저장 ──────────────────────────────────────────────────
brief_fn = f"brief_{today_str}.html"
with open(brief_fn, "w", encoding="utf-8") as f:
    f.write(brief_html(sections, keywords, signals))
print(f"[DONE] {brief_fn} 저장")

BRIEFS_JSON = "briefs.json"
try:
    with open(BRIEFS_JSON,"r",encoding="utf-8") as f: briefs=json.load(f)
except: briefs=[]
briefs=[b for b in briefs if b.get("date")!=today_str]
briefs.insert(0,{"date":today_str,"edition":edition,"filename":brief_fn,"keywords":keywords})
briefs=briefs[:20]
with open(BRIEFS_JSON,"w",encoding="utf-8") as f:
    json.dump(briefs,f,ensure_ascii=False,indent=2)
print(f"[DONE] briefs.json ({len(briefs)}개)")

with open("index.html","w",encoding="utf-8") as f:
    f.write(index_html(briefs))
print("[DONE] index.html")
