# 📰 AI 크리에이티브 위클리 브리프 — 자동화 설정 가이드

GitHub Actions + Claude API + Tavily로 매주 월·목 자동 생성되는 AI 브리프입니다.
완전 무료(또는 매우 저비용)로 운영할 수 있습니다.

---

## 📁 파일 구조

```
your-repo/
├── .github/
│   └── workflows/
│       └── ai-brief.yml      ← GitHub Actions 스케줄러
├── generate_brief.py          ← 검색 + AI 생성 스크립트
├── index.html                 ← 자동 생성되는 결과물 (GitHub Pages)
└── README.md
```

---

## 🚀 설정 단계 (5단계)

### 1단계 — GitHub 저장소 생성

1. GitHub에서 새 저장소(Repository) 생성
   - 이름 예: `ai-weekly-brief`
   - **Public**으로 설정 (GitHub Pages 무료 사용 조건)
2. 이 폴더의 파일 전체를 저장소에 업로드

```bash
git init
git add .
git commit -m "Initial setup"
git remote add origin https://github.com/YOUR_USERNAME/ai-weekly-brief.git
git push -u origin main
```

---

### 2단계 — Claude API 키 발급

1. [console.anthropic.com](https://console.anthropic.com) 접속 → 회원가입
2. **API Keys** 메뉴 → **Create Key**
3. 키 복사해 두기 (`sk-ant-...` 형태)

> 💡 **비용 참고**: claude-sonnet-4-6 기준 브리프 1회 생성 시 약 $0.01~0.03 (월 8회 = 약 $0.1~0.3)

---

### 3단계 — Tavily API 키 발급 (웹 검색)

1. [tavily.com](https://app.tavily.com) 접속 → 회원가입
2. 대시보드에서 API 키 복사 (`tvly-...` 형태)

> 💡 **무료 플랜**: 월 1,000회 검색 제공 (브리프 1회당 약 8회 사용 → 월 125회 여유)

---

### 4단계 — GitHub Secrets 등록

저장소 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret 이름 | 값 |
|-------------|-----|
| `ANTHROPIC_API_KEY` | `sk-ant-...` |
| `TAVILY_API_KEY` | `tvly-...` |

---

### 5단계 — GitHub Pages 활성화

저장소 → **Settings** → **Pages**
- Source: **Deploy from a branch**
- Branch: `main` / `/ (root)`
- **Save** 클릭

약 2~3분 후 `https://YOUR_USERNAME.github.io/ai-weekly-brief/` 에서 확인 가능

---

## ⚙️ 자동 실행 스케줄

| 요일 | 실행 시각 (KST) | 수집 기간 |
|------|----------------|-----------|
| 월요일 | 오전 9:00 | 직전 4일 |
| 목요일 | 오전 9:00 | 직전 3일 |

---

## 🧪 수동 테스트 실행

저장소 → **Actions** 탭 → **AI Creative Weekly Brief** → **Run workflow** → **Run workflow** 버튼

---

## 🔧 커스터마이징

`generate_brief.py` 상단의 `SEARCH_QUERIES` 딕셔너리를 수정하면
검색 키워드를 자유롭게 바꿀 수 있습니다.

```python
SEARCH_QUERIES = {
    "Video AI": [
        "video AI generation tools news March 2026",
        ...
    ],
    ...
}
```

---

## ❓ 문제 해결

| 증상 | 해결 방법 |
|------|-----------|
| Actions가 실행되지 않음 | Settings → Actions → General → Allow all actions 확인 |
| index.html이 업데이트 안 됨 | Secrets 값 재확인, Actions 로그 확인 |
| GitHub Pages가 보이지 않음 | Pages 설정에서 branch가 `main`인지 확인 |
| API 오류 | Claude/Tavily 키 유효성 및 크레딧 잔액 확인 |
