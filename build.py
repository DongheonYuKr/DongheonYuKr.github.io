#!/usr/bin/env python3
"""HEONLOG 안내 사이트 만들기. content/*.html(맨 위 --- 칸) → guide/<slug>/index.html + 첫 화면·소개·sitemap.
새 글: content/에 파일 하나 추가 → python3 build.py
"""
import base64, hashlib
import html, json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://heonlog.com"  # 주소가 정해지면 여기만 바꾼다 (끝에 / 없이)
SITE = "HEONLOG 가이드"
CSS_V = __import__("hashlib").sha256(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css"), "rb").read()).hexdigest()[:8]
POSTYPE = "https://www.postype.com/@heonlog/post/23525235"
SOCIAL = ('<a href="https://www.instagram.com/heonlog.studio/" rel="noopener noreferrer">인스타그램</a>'
          '<a href="https://www.threads.com/@heonlog.studio" rel="noopener noreferrer">스레드</a>'
          '<a href="https://www.youtube.com/@heonlog.studio" rel="noopener noreferrer">유튜브</a>'
          '<a href="https://www.tiktok.com/@heonlog" rel="noopener noreferrer">틱톡</a>'
          '<a href="https://www.linkedin.com/company/heonlog/" rel="noopener noreferrer">링크드인</a>')
CTA = ''  # 대표님 10-30: 「~보내 주시면 드립니다」 같은 주는 약속 문구 넣지 않음
# 10-31: 주는 약속 없이 길 안내만 · 11-01: 「소식받기」(인포크 기능과 헷갈림) 빼고 인스타 한 줄로 — 첫 화면·/free/ 끝
NEXT = ('<aside class="cta" aria-label="다음 회"><p><strong>다음 깃허브 털기도 보고 싶다면</strong> · '
        '다음 회차는 인스타그램 <a href="https://www.instagram.com/heonlog.studio/" rel="noopener">@heonlog.studio</a>에 먼저 올라옵니다.</p></aside>')
# 11-01 무료·유료 경계 보고서 4절 A(정리본 판매 전 판): 가이드 끝 3층 안내 — 아직 없는 링크·결제 버튼·신청서는 만들지 않음.
# 정리본 판매 시작(11-08 예정) 때 셋째 줄에 링크, 신청서 연 날(11-15~) 둘째 줄에 신청 링크를 붙인다.
GUIDE_NEXT = ('<aside class="nextstep" aria-label="다음 단계"><p class="ns-h">여기까지 따라 하셨다면, 다음은</p><div class="ns-grid">'
              '<a class="ns y" href="../../kit/"><span class="k">무료</span><b>깔기 전 시작 키트 10쪽</b><span>어느 도구든 깔기 전에 볼 것 전부 · 직접 깔아 본 12개 결과표</span><span class="go">바로 받기 →</span></a>'
              f'<a class="ns dk" href="{POSTYPE}" rel="noopener noreferrer"><span class="k">정리본 · 3,900원</span><b>깃허브 털기 #01~#05 한 파일로</b><span>회차마다 붙여 넣을 문장 · 막혔을 때 문장 · 한 쪽 요약</span><span class="go">미리 보기 →</span></a>'
              '<a class="ns" href="../../work/repurpose/"><span class="k">사업자라면</span><b>영상 1편으로 한 달 SNS 채우기</b><span>찍어 둔 영상만 보내세요 · 쇼츠·카드뉴스·블로그·SNS 글</span><span class="go">작업 예시와 가격 →</span></a>'
              '</div><p class="ns-foot">다음 회차는 인스타그램 <a href="https://www.instagram.com/heonlog.studio/" rel="noopener noreferrer">@heonlog.studio</a>에 먼저 올라옵니다.</p></aside>')
# 11-01 회차 글 새 틀(디립다식): 위에 맡기기 줄 · 주의 상자, 끝에 깃허브 설치 명령(복사) · 묻고 답한 것
# 명령은 각 README 2026-11-01 기준. README가 바뀌면 여기만 고친다.
INSTALL = {
    "github-archify": ("AI 비서에게 보내는 한 문장", "Install Archify for me by reading https://raw.githubusercontent.com/tt-a1i/archify/main/llms.txt"),
    "github-agent-reach": ("README의 한 문장(중국어로 「Agent Reach 깔아 줘」) · PyPI의 같은 이름 패키지는 이 프로젝트가 아니에요", "帮我安装 Agent Reach：https://raw.githubusercontent.com/Panniantong/Agent-Reach/main/docs/install.md"),
    "github-hyperframes": ("클로드 코드용 명령 2줄 · 한 줄씩 따로 · 제가 깔 때는 npx 명령이었는데 지금 README는 이 2줄이에요", "claude plugin marketplace add heygen-com/hyperframes\nclaude plugin install hyperframes@hyperframes"),
    "github-taste-skill": ("쓸 작업 폴더에서 클로드 코드를 열고 한 줄", 'npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"'),
}
GUIDE_TOP = ('<p class="warnbox"><b>⚠ 채팅 창이 아니라 클로드 코드 입력창입니다</b>클로드 데스크톱 앱의 「Code」 탭이나 터미널에서 claude를 친 뒤 나오는 입력창에 붙여 넣어야 깔립니다. 클로드 유료 구독(Pro · 월 20달러부터)이 필요합니다.</p>\n')
WORK_LINE = '<a class="workline" href="../../work/"><span>직접 깔기 벅차면, 사업자용 페이지·광고 제작은 맡길 수도 있어요</span><b>맡기기 →</b></a>\n'
COPY_JS = ("<script>document.querySelectorAll('.cmdbox button').forEach(function(b){b.addEventListener('click',function(){"
           "var t=b.closest('.cmdbox').querySelector('code').textContent;navigator.clipboard.writeText(t).then(function(){b.textContent='복사됨'},"
           "function(){var r=document.createRange();r.selectNodeContents(b.closest('.cmdbox').querySelector('code'));var s=getSelection();s.removeAllRanges();s.addRange(r);b.textContent='선택됨 · ⌘C'})})})</script>")
QA = ('<section class="qa" aria-label="묻고 답한 것"><h2>묻고 답한 것</h2><p>막힌 곳은 이 회차 인스타그램 게시물에 댓글이나 DM으로 남겨 주세요. 여러 분이 같은 데서 막히면 답을 여기에 정리해 둡니다.</p>'
      '<p class="empty">아직 정리한 질문이 없어요.</p><p><a class="btn ghost" href="https://www.instagram.com/heonlog.studio/" rel="noopener noreferrer">인스타그램에서 질문하기 →</a></p></section>\n')


# 예전 뷰티 글: 지우거나 숨기지 않고(주소·사이트맵 그대로) 글 맨 위에 「예전 글」 표시만 · 11-01
OLD_NOTE = ('<p class="notice oldnote"><strong>예전 글</strong> · 2026년 10월, 작은 뷰티 브랜드 광고 소재를 만들 때 정리한 글입니다. '
            '법·제도 내용은 쓴 날짜 기준이니 최신 원문으로 다시 확인하세요. 지금 HEONLOG는 <a href="../../">「깃허브 털기」</a>를 연재합니다. 이 주제(제품 화보·모델컷·상세페이지·광고 문구 점검)로 작업을 맡기고 싶다면 <a href="../../work/">맡기기</a>를 봐 주세요.</p>\n')


# 맡기기 문의 = 인포크 「비즈니스 제안」 하나로 (이메일 주소는 페이지에 쓰지 않음 · 11-01)
INPOCK_BTN = ('<p class="ask"><a class="btn" href="https://link.inpock.co.kr/heonlog" rel="noopener">인포크 「비즈니스 제안」으로 문의하기</a>'
              '<span>링크 페이지의 「비즈니스 제안」 버튼에서 남길 수 있습니다. 결제는 이 사이트에서 받지 않습니다.</span></p>')
# (주소, 본문 파일, 제목, 설명, 메뉴 칸)
WORK_PAGES = [
    ("kit/", "_kit.part", "무료 시작 키트: 깃허브 도구 깔기 전에 볼 것 전부",
     "깃허브 무료 도구 12개를 직접 깔아 보며 겪은 것 — 저장소 읽기·확인 4가지·멈춤 신호·묻는 문장·결과표. 10쪽 PDF, 이메일·가입 없이 무료.", "free"),
    ("work/subscription/", "_work_subscription.part", "AI 구독비 다이어트 30분 진단",
     "지금 쓰는 유료 AI·디자인 구독 목록을 계속 쓸 것·싼 요금제·무료 대안·안 써도 되는 것으로 나눈 1쪽 표와 30분 화상 설명. 시범 가격 19,000원.", "work"),
    ("work/repurpose/", "_work_repurpose.part", "영상 1편으로 한 달 SNS 채우기",
     "찍어 둔 영상 한 편을 세로 쇼츠 3개·카드뉴스 6장·블로그 글·SNS 글 4개로. 단건 129,000원 · 월 4편 390,000원(오픈 가격 첫 5건).", "work"),
    ("work/english/", "_work_english.part", "제품 영상, 해외 판매용 영어판으로",
     "한국어 제품·광고 영상을 영어 자막·화면 글자·영어 제목·설명까지 맞춘 해외 판매용 영어판으로. 49,000원부터(오픈 가격 첫 5건).", "work"),
    ("tools/cost/", "_tools_cost.part", "AI 구독료 계산기",
     "쓰는 AI 구독에 체크하면 한 달·1년 합계가 나옵니다. 요금은 공식 요금 페이지에서 확인한 것만, 확인 날짜와 함께 넣었습니다. 저장·쿠키 없음.", ""),
    # 11-01 E1 시제품: 직접 깔아 본 기록에서만 판정(AI 호출·서버 없음), 없으면 「깔기 전 확인 3가지」
    ("tools/check/", "_tools_check.part", "이 깃허브 도구, 나도 깔 수 있을까? 설치 판정",
     "깃허브 주소를 넣으면 직접 깔아 본 기록에서 준비물·난이도·함정을 보여 줍니다. 안 깔아 본 도구는 판정하지 않고 깔기 전 확인 3가지만 안내합니다. 참고용·결과 보장 없음.", ""),
]

# 영어 페이지 (주소, 본문 파일, 제목, 설명, 메뉴 칸, 짝 한국어 주소 또는 None, schema 종류) · 11-01
EN_PAGES = [
    ("en/", "_en_home.part", "Free GitHub tools, installed and rated by a non-developer",
     "I have AI install free GitHub tools instead of paid ones, then rate install difficulty (click only to gave up), what broke, and the catch.",
     "home", "", "WebPage"),
    ("en/guide/archify/", "_en_guide_archify.part", "How to use archify: turn a hard-to-explain workflow into one picture · GitHub Teardown #01",
     "I had AI install the free GitHub tool archify. What it does, why the install difficulty is ⭐⭐⭐, where I got stuck, and the catch before you use it.",
     "", "guide/github-archify/", "Article"),
    ("en/free/", "_en_free.part", "Free GitHub alternatives to monthly-subscription tools: a preview",
     "A preview of free GitHub tools that do a similar job to paid subscription tools: 3 tools I actually installed, with the kind of paid tool each replaces and install difficulty.",
     "free", "free/", "WebPage"),
    ("en/work/english-product-copy/", "_en_work_product_copy.part", "Korean beauty & lifestyle product copy, written for US shoppers",
     "English product listing copy for sellers of Korean beauty and lifestyle products: title, bullets, description, how to use. Three fictional samples and a pilot price in USD.",
     "work", None, "WebPage"),
]
EN_ALT = {ko: en for en, _, _, _, _, ko, _ in EN_PAGES if ko and ko not in ("", "free/")}


def practice(slug):
    """11-01 대표님 「무료 자료 양질로」: content/_practice_<slug>.part 가 있으면 회차 글 맨 위에 실전 따라 하기를 붙인다(설치 명령 칸은 그 안에)."""
    f = os.path.join(ROOT, "content", f"_practice_{slug}.part")
    return open(f, encoding="utf-8").read() if os.path.exists(f) else ""


def install_box(slug):
    if slug not in INSTALL or practice(slug):
        return ""
    note, cmd = INSTALL[slug]
    return (f'<h2>깃허브에 적힌 설치 명령</h2><p class="meta">{html.escape(note)} · 2026-11-01 기준, 바뀔 수 있어요 · 붙여 넣기 전에 <a href="../../kit/">시작 키트</a>의 확인 문장부터</p>'
            f'<div class="cmdbox"><div class="bar"><span>설치 명령</span><button type="button">복사</button></div><code>{html.escape(cmd)}</code></div>\n{COPY_JS}\n')


def read_articles():
    out = []
    for name in sorted(os.listdir(os.path.join(ROOT, "content"))):
        # 「_」로 시작하는 파일(_draft_… 미리 써 둔 글, _about.part 등)은 글 목록·주소에서 뺀다 (11-01)
        if not name.endswith(".html") or name.startswith("_"):
            continue
        raw = open(os.path.join(ROOT, "content", name), encoding="utf-8").read()
        m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
        meta = dict(l.split(": ", 1) for l in m.group(1).splitlines() if ": " in l)
        meta["body"] = m.group(2)
        meta["slug"] = name[:-5].split("_", 1)[1]
        out.append(meta)
    return out


def page(title, desc, path, body, depth, og_image="img/og.jpg", og_type="website", jsonld=None, current="",
         lang="ko", alt=None, notfound=False, published=None, wide=False):
    """lang="en" = 영어 페이지(메뉴·아래줄 영어) · alt = 짝 언어 페이지 주소(hreflang·「한국어」/「EN」 링크) · 11-01
    notfound=True = 404 페이지: 어느 깊이의 주소에서 떠도 디자인이 깨지지 않게 「/」로 시작하는 절대 주소 · canonical 없이 noindex (11-01)
    사이트 안 링크는 대표 주소(canonical)와 같게 폴더 주소(…/)로 — 「…/index.html」로 걸지 않는다 (11-01 SEO 점검 2번)"""
    up = "/" if notfound else "../" * depth
    canon = f"{BASE_URL}/{path}"
    hl = ""
    if alt is not None:
        ko_p, en_p = (path, alt) if lang == "ko" else (alt, path)
        hl = (f'<link rel="alternate" hreflang="ko" href="{BASE_URL}/{ko_p}">\n'
              f'<link rel="alternate" hreflang="en" href="{BASE_URL}/{en_p}">\n'
              f'<link rel="alternate" hreflang="x-default" href="{BASE_URL}/{ko_p}">\n')
    other = (up + (alt if alt is not None else ("en/" if lang == "ko" else ""))) or "./"
    nav = lambda href, label, key, extra="": f'<a href="{(up + href) or "./"}"{" aria-current=\"page\"" if current == key else ""}{extra}>{label}</a>'
    if lang == "en":
        top = (f'<a class="skip" href="#main">Skip to content</a>\n<header class="site"><div class="wrap">\n'
               f'<a class="logo" href="{up}en/" aria-label="HEONLOG home (English)"><img src="{up}img/logo.svg" alt="HEONLOG" width="104" height="26"></a>\n'
               f'<nav class="top" aria-label="Main menu">{nav("en/", "Guides", "home")}{nav("en/free/", "Free preview", "free")}'
               f'{nav("en/work/english-product-copy/", "Hire", "work")}'
               f'<a class="lang" href="{other}" lang="ko" hreflang="ko">한국어</a></nav>\n</div></header>')
        foot = (f'<footer class="site"><div class="wrap">\n<p>HEONLOG · GitHub tools, installed by a non-developer · Instagram '
                f'<a href="https://www.instagram.com/heonlog.studio/" rel="noopener">@heonlog.studio</a> (in Korean) · Business inquiries: the '
                f'&ldquo;Business proposal&rdquo; button on my <a href="https://link.inpock.co.kr/heonlog" rel="noopener">link page</a></p>\n'
                f'<p>Nothing here is legal advice. Check the official sources before you rely on it. · '
                f'<a href="{up}about/#privacy" lang="ko" hreflang="ko">Privacy &amp; terms (Korean)</a> · '
                f'<a href="{other}" lang="ko" hreflang="ko">한국어</a></p>\n</div></footer>')
    else:
        top = (f'<a class="skip" href="#main">본문 바로가기</a>\n<header class="site"><div class="wrap">\n'
               f'<a class="logo" href="{up or "./"}" aria-label="HEONLOG 첫 화면"><img src="{up}img/logo.svg" alt="HEONLOG" width="104" height="26"></a>\n'
               f'<nav class="top" aria-label="주 메뉴">{nav("", "게시물", "home")}{nav("free/", "무료 자료", "free")}'
               f'<a href="{POSTYPE}" rel="noopener noreferrer">정리본</a>'
               f'{nav("work/", "맡기기", "work")}{nav("about/", "소개", "about")}'
               f'<a class="navcta" href="{up}kit/">무료 시작 키트 →</a></nav>\n</div></header>')
        foot = (f'<footer class="site"><div class="wrap">\n<div class="fcols">'
                f'<div><span class="brand">HEONLOG</span><span>개발 몰라도 깃허브 털기</span></div>'
                f'<div><span class="h">채널</span>{SOCIAL}</div>'
                f'<div><span class="h">안내</span><a href="{up}about/#privacy">이용 안내</a><a href="{up}about/#privacy">개인정보 처리 안내</a><a href="{up}kit/">무료 시작 키트</a></div>'
                f'<div><span class="h">문의</span><a href="https://link.inpock.co.kr/heonlog" rel="noopener noreferrer">인포크 「비즈니스 제안」</a><a href="https://www.instagram.com/heonlog.studio/" rel="noopener noreferrer">인스타그램 DM</a></div>'
                f'</div>\n<p class="legal">이 사이트에서는 결제를 받지 않습니다. 판매와 결제는 크몽 · 포스타입에서 이뤄지며, 환불은 각 플랫폼 기준을 따릅니다. '
                f'글 속 법·제도 내용은 정리일 뿐 법률 자문이 아닙니다.<br>© 2026 HEONLOG · 모든 설치와 실행은 본인 컴퓨터에서 본인이 하며, 결과를 보장하지 않습니다.</p>\n</div></footer>')
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    head_url = '<meta name="robots" content="noindex">\n' if notfound else f'<link rel="canonical" href="{canon}">\n'
    og_url = "" if notfound else f'<meta property="og:url" content="{canon}">\n'
    # 글마다 만든 가로 1200×630 대표 그림(img/og/·img/og.jpg)이면 크기도 알려 준다
    og_size = ('<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
               if og_image.startswith("img/og") else "")
    pub = f'<meta property="article:published_time" content="{published}">\n' if published else ""
    # 보안(11-01): 이 페이지 안 인라인 스크립트만 해시로 허용 · 바깥은 Cloudflare 통계 하나 · 폼 전송·다른 사이트 끼워 넣기 막음
    inl = re.findall(r"<script>(.*?)</script>", body, re.S)
    hashes = " ".join("'sha256-" + base64.b64encode(hashlib.sha256(x.encode("utf-8")).digest()).decode() + "'" for x in inl)
    csp = ("default-src 'self'; script-src 'self' https://static.cloudflareinsights.com " + hashes +
           "; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' https://cdn.jsdelivr.net data:; "
           "img-src 'self' data: https:; connect-src 'self' https://cloudflareinsights.com; "
           "object-src 'none'; base-uri 'self'; form-action 'none'; upgrade-insecure-requests")
    sec = (f'<meta http-equiv="Content-Security-Policy" content="{csp}">\n'
           '<meta name="referrer" content="strict-origin-when-cross-origin">\n')
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta name="naver-site-verification" content="532f68a567a7bab22e3a75b82164f1a44f273f91">
<meta name="naver-site-verification" content="8a65c8d4b155d54f1e5790ab92ae384083104cec">
<meta name="google-site-verification" content="vj1r-xyzpSqau7A590A6hj5wXop7oyVEvwiRU8IKaeU">
<meta charset="utf-8">
{sec}<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
{head_url}{hl}<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{"HEONLOG" if lang == "en" else SITE}">
<meta property="og:locale" content="{"en_US" if lang == "en" else "ko_KR"}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
{og_url}<meta property="og:image" content="{BASE_URL}/{og_image}">
{og_size}{pub}
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="{up}img/favicon.png">
<link rel="apple-touch-icon" href="{up}img/icon-180.png">
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="stylesheet" href="{up}style.css?v={CSS_V}">
{ld}
<!-- Cloudflare Web Analytics (쿠키 없는 방문 수 · 11-01) --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "9f4bf7e4514c4afc99a713798af12a04"}}'></script><!-- End Cloudflare Web Analytics -->
</head>
<body>
{top}
<main id="main"><div class="wrap{" wide" if wide else ""}">
{body}
</div></main>
{foot}
</body>
</html>
"""


def main():
    arts = read_articles()
    org = {"@type": "Organization", "name": "HEONLOG", "url": BASE_URL + "/",
           "sameAs": ["https://www.instagram.com/heonlog.studio/"]}
    newest = max(a.get("updated", a["date"]) for a in arts)  # 첫 화면·소개 lastmod = 가장 최근에 고친 글 날짜
    urls = [("", newest), ("about/", newest), ("free/", "2026-11-01")]
    # 깃허브 털기 회차 순서(파일 번호 순) — 글 끝 「같이 보면 좋은 글」에 이전·다음 회 + 무료 맛보기 (11-01 SEO 점검 회차 틀)
    series = [x for x in arts if x["slug"].startswith("github-")]
    for a in arts:
        path = f"guide/{a['slug']}/"
        img = a.get("image", "img/og.jpg")
        updated = a.get("updated", a["date"])
        graph = [{"@type": "Article", "headline": a["title"], "description": a["description"],
                  "datePublished": a["date"], "dateModified": updated, "inLanguage": "ko", "image": [f"{BASE_URL}/{img}"],
                  "author": org, "publisher": org, "mainEntityOfPage": f"{BASE_URL}/{path}", "keywords": a["keyword"]},
                 {"@type": "BreadcrumbList", "itemListElement": [
                     {"@type": "ListItem", "position": 1, "name": "가이드", "item": f"{BASE_URL}/"},
                     {"@type": "ListItem", "position": 2, "name": a["kicker"], "item": f"{BASE_URL}/{path}"}]}]
        # 본문에 <section class="faq"> (h3 질문 + p 답)가 실제로 있을 때만 FAQPage
        faq = re.findall(r'<section class="faq">(.*?)</section>', a["body"], re.S)
        if faq:
            qa = re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", faq[0], re.S)
            graph.append({"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": html.unescape(re.sub("<.*?>", "", q)),
                 "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re.sub("<.*?>", "", ans))}} for q, ans in qa]})
        ld = {"@context": "https://schema.org", "@graph": graph}
        related = ""
        if a in series:
            i = series.index(a)
            rel = ([("이전 회", series[i - 1])] if i > 0 else []) + ([("다음 회", series[i + 1])] if i + 1 < len(series) else [])
            related = ('<nav class="related" aria-label="같이 보면 좋은 글"><h2>같이 보면 좋은 글</h2>\n<ul>\n'
                       + "".join(f'<li><span>{lb}</span> <a href="../{r["slug"]}/">{html.escape(r["title"])}</a></li>\n' for lb, r in rel)
                       + '<li><span>모아 보기</span> <a href="../../free/">유료 대신 무료 맛보기: 직접 깔아 본 깃허브 무료 대안</a></li>\n</ul></nav>\n')
        upd = f' · 고친 날 {updated.replace("-", ".")}' if updated != a["date"] else ""
        body = (f'<article><p class="meta"><span class="kicker">{html.escape(a["kicker"])}</span> · '
                f'<time datetime="{a["date"]}">{a["date"].replace("-", ".")}</time>{upd} · HEONLOG</p>\n<h1>{html.escape(a["title"])}</h1>\n'
                + ((WORK_LINE + GUIDE_TOP + practice(a["slug"]) + (COPY_JS if practice(a["slug"]) else "")) if a["slug"].startswith("github-") else OLD_NOTE)
                + a["body"].replace("{{up}}", "../../") + "\n" + install_box(a["slug"])
                + (QA if a["slug"].startswith("github-") else "") + related + (GUIDE_NEXT if a["slug"].startswith("github-") else CTA) + "</article>")
        os.makedirs(os.path.join(ROOT, path), exist_ok=True)
        open(os.path.join(ROOT, path, "index.html"), "w", encoding="utf-8").write(
            page(f'{a["title"]} | {SITE}', a["description"], path, body, 2,
                 og_image=img, og_type="article", jsonld=ld, alt=EN_ALT.get(path), published=a["date"]))
        urls.append((path, updated))

    li = lambda a: f'<li><a href="guide/{a["slug"]}/">{html.escape(a["title"])}</a><p>{html.escape(a["description"])}</p></li>'
    gh = sorted([a for a in arts if a["slug"].startswith("github-")], key=lambda a: (a.get("date", ""), a["slug"]), reverse=True)
    old = [a for a in arts if not a["slug"].startswith("github-")]
    # 11-01 새 첫 화면(디립다식 · 시안 승인): 프로필 → 시작 키트 띠 → 탭(CSS만, JS 없음) → 카드판 → 맡기기 띠
    # 잠금 카드 = 인스타 운영표 날짜. 그날 글이 올라오면 이 줄에서 빼고 content/에 글을 넣는다.
    LOCKED = [("#06", "11-09(월)"), ("#07", "11-10(화)"), ("#08", "11-12(목)")]
    E = html.escape
    card = lambda cls, href, k, title, d: f'<a class="card {cls}" href="{href}"><span class="k">{k}</span><span><b>{E(title)}</b><span class="d">{E(d)}</span></span></a>'
    SHORT = {"github-archify": ("GITHUB #01", "archify — 설명을 그림 한 장으로", "새 버전 확인은 껐어요 · ⭐⭐⭐"),
             "github-agent-reach": ("GITHUB #02", "Agent-Reach — 유튜브 자막·웹 글 읽어 오기", "기능 17개 중 13개 작동 · ⭐⭐⭐"),
             "github-hyperframes": ("GITHUB #03", "hyperframes — 화면을 영상 파일로", "유료 키 없이 릴스 37초 · ⭐⭐⭐"),
             "github-taste-skill": ("GITHUB #04", "taste-skill — AI 티 나는 디자인 피하기", "폴더 하나에만 깔려요 · ⭐⭐⭐"),
             "github-voicestudio": ("GITHUB #05", "VoiceStudio 💀 — 깔고 지운 도구", "내 목소리 복제 · 녹음을 못한 탓도 큼")}
    ghc = [card("gh", f'guide/{x["slug"]}/', *SHORT.get(x["slug"], ("GITHUB", x["title"], x.get("keyword", "")))) for x in gh]
    lockc = "".join(f'<div class="card gh lock" aria-label="깃허브 털기 {n} · {d} 공개 예정"><span class="top"><span class="k">GITHUB {n}</span><span class="when">🔒 {d} 공개</span></span>'
                    f'<span><b aria-hidden="true">다음 도구 이름이 여기에</b><span class="d">인스타에 먼저 올라가요 · 팔로우하면 먼저 봐요</span></span></div>' for n, d in LOCKED)
    cards = (card("free y", "kit/", "FREE · 무료 자료", "깔기 전 시작 키트 10쪽", "어느 도구든 깔기 전에 · 이메일·가입 없이")
             + f'<a class="card dk" href="{POSTYPE}" rel="noopener noreferrer"><span class="k">EBOOK · 정리본</span><span><b>깃허브 털기 정리본 v2 (#01~#05)</b><span class="d">붙여 넣을 문장까지 · 3,900원 · 포스타입</span></span></a>'
             + lockc + "".join(ghc)
             + card("free", "free/", "FREE · 무료 자료", "유료 대신 무료 맛보기", "월 구독 도구의 깃허브 무료 대안")
             + card("work", "work/", "WORK · 맡기기", "사업자용 작업 예시 4가지", "광고 영상 · 상세페이지 · 카드뉴스 · 영문 상품 설명")
             + "".join(card("old", f'guide/{x["slug"]}/', "예전 글", x["title"], x.get("keyword", "")) for x in old))
    home = f"""<section class="hero"><img src="img/profile.jpg" alt="HEONLOG 프로필 그림" width="112" height="112">
<div><p class="mono">HEONLOG · 개발 몰라도 깃허브 털기</p><h1>유료 AI 대신, 무료 깃허브 도구를<br>직접 깔아 보고 알려 드려요</h1></div></section>
<a class="kitstrip" href="kit/"><span><b>깔기 전 시작 키트 · 무료 10쪽</b><span class="s">저장소 읽는 법 · 확인 4가지 · 멈춤 신호 · 직접 깔아 본 12개 결과표</span></span><span class="go">바로 받기 →</span></a>
<div class="tabs">
<input type="radio" name="tab" id="t-all" checked><input type="radio" name="tab" id="t-gh"><input type="radio" name="tab" id="t-free"><input type="radio" name="tab" id="t-old">
<div class="tabbar" role="group" aria-label="게시물 종류"><label for="t-all">전체</label><label for="t-gh">깃허브 털기 <small>{len(gh)} + 공개 예정 {len(LOCKED)}</small></label><label for="t-free">무료 자료 <small>2</small></label><label for="t-old">예전 글 <small>{len(old)}</small></label></div>
<div class="cards">
{cards}
</div>
</div>
<div class="workstrip"><span><b>사업자라면 · 맡기기</b><span class="s">세로 광고 영상 · 상세페이지 시안 · 카드뉴스 · 영문 상품 설명 — 주문은 크몽에서</span></span><a href="work/">작업 예시와 가격 보기 →</a></div>"""
    site_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": BASE_URL + "/",
               "inLanguage": "ko", "publisher": org}
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(
        page("HEONLOG · 개발 몰라도 깃허브 털기",
             "유료 AI 대신 무료 깃허브 도구를 개발을 모르는 사람이 직접 깔아 보고 기록합니다. 깔기 전 시작 키트(무료 10쪽)와 회차별 정리본, 사업자용 맡기기.",
             "", home, 0, jsonld=site_ld, current="home", alt="en/", wide=True))

    about = open(os.path.join(ROOT, "content", "_about.part"), encoding="utf-8").read()
    os.makedirs(os.path.join(ROOT, "about"), exist_ok=True)
    open(os.path.join(ROOT, "about", "index.html"), "w", encoding="utf-8").write(
        page(f"소개: 개발 몰라도 깃허브 털기, HEONLOG | {SITE}",
             "HEONLOG는 개발을 모르는 사람이 깃허브 무료 도구를 AI로 직접 깔아 보고 기록하는 곳입니다. 직접 해 본 것과 공식 출처로 확인한 것만 씁니다.",
             "about/", about + CTA, 1, jsonld={"@context": "https://schema.org", "@type": "AboutPage", "name": "HEONLOG 소개", "publisher": org},
             current="about"))

    # 11-01 대표님 「무료 대체표 알려 주면 콘텐츠 뺏기는 것」 → /free/·/en/free/는 깔아 본 것 3줄 맛보기만.
    # 원본 20줄은 content/_free_full20.part · _en_free_full20.part(.gitignore — 공개 저장소에도 안 올라감). 정리본 판매(11-08 예정) 전엔 링크·결제 버튼 없음.
    free = open(os.path.join(ROOT, "content", "_free.part"), encoding="utf-8").read().replace(
        "{{guides}}", "\n".join(f'<li><a href="../guide/{a["slug"]}/">{html.escape(a["title"])}</a></li>'
                                 for a in sorted(gh, key=lambda a: (a.get("date", ""), a["slug"]))))
    os.makedirs(os.path.join(ROOT, "free"), exist_ok=True)
    open(os.path.join(ROOT, "free", "index.html"), "w", encoding="utf-8").write(
        page(f"유료 대신 무료 맛보기: 월 구독 도구의 깃허브 무료 대안 | {SITE}",
             "월 구독 도구 대신 쓸 수 있는 깃허브 무료 도구 맛보기. 직접 깔아 본 3개를 대신하는 유료 도구 종류·설치 난이도와 함께 보여 드립니다.",
             "free/", free + NEXT, 1, jsonld={"@context": "https://schema.org", "@type": "WebPage", "name": "유료 대신 무료 맛보기",
                                              "inLanguage": "ko", "publisher": org}, current="free", alt="en/free/"))

    # 맡기기(/work/) 소개 페이지 + 무료 계산기(/tools/cost/) · 11-01. 본문은 content/_work*.part · _tools_cost.part
    for path, part, title, desc, key in WORK_PAGES:
        body = open(os.path.join(ROOT, "content", part), encoding="utf-8").read().replace("{{inpock}}", INPOCK_BTN)
        os.makedirs(os.path.join(ROOT, path), exist_ok=True)
        open(os.path.join(ROOT, path, "index.html"), "w", encoding="utf-8").write(
            page(f"{title} | {SITE}", desc, path, body, path.count("/"),
                 jsonld={"@context": "https://schema.org", "@type": "WebPage", "name": title,
                         "inLanguage": "ko", "publisher": org}, current=key))
        urls.append((path, "2026-11-01"))

    # 맡기기(/work/) · 11-01 새 화면(시안 승인): 크몽 기본 패키지 기준 사실만 · 모르는 칸은 「크몽 상품 페이지」로
    svc = [("01 · 광고 영상", "제품 사진으로 세로 광고 영상", "svc-ad.jpg", "세로 광고 영상 작업 예시 (SAMPLE)",
            "촬영 일정 없이 광고 소재가 급한 작은 브랜드, 메타·틱톡 광고를 여러 버전 시험하는 마케터", 49000, 39000,
            [("기본 패키지", "10초 · 장면 2개 · 자막"), ("작업 기간", "3일"), ("수정", "1회 (표준·고급 2회)")]),
           ("02 · 상세페이지", "상세페이지 첫 화면 시안", "svc-detail.jpg", "상세페이지 첫 화면 시안 작업 예시 (SAMPLE)",
            "스마트스토어·쿠팡 상세페이지의 첫 화면(제일 먼저 보이는 한 장)을 바꾸고 싶은 셀러", 39000, 29000,
            [("기본 패키지", "첫 화면 2안"), ("작업 기간", "2일"), ("수정", "고른 1안 기준 1회")]),
           ("03 · 카드뉴스", "정보형 카드뉴스 · 인스타 캐러셀", "svc-carousel.jpg", "카드뉴스 작업 예시 (SAMPLE)",
            "글·영상·자료는 있는데 저장되는 카드뉴스로 바꿀 시간이 없는 브랜드 계정", 49000, 29000,
            [("기본 패키지", "6장 · 문장은 주신 대로"), ("작업 기간", "2일"), ("수정", "크몽 상품 페이지에")]),
           ("04 · 영문 상품 설명", "해외 판매용 영문 상품 설명", "svc-listing.jpg", "영문 상품 설명 작업 예시 (SAMPLE)",
            "한국 상품을 아마존·쇼피파이 등에 올리는 셀러 — 한국어 원문을 영어 리스팅으로", 59000, 39000,
            [("기본 패키지", "크몽 상품 페이지에"), ("작업 기간", "1일"), ("수정", "크몽 상품 페이지에")]),
           # 11-01 밤 새 상품 2개 (크몽 #852900 · #852910 승인 대기) · 할인 표시 없음
           ("05 · 광고 소재 묶음", "광고 소재 10개 + 반응 비교 보고", "svc-ad10.jpg", "광고 소재 묶음 작업 예시 (SAMPLE · 가상 브랜드)",
            "메타·인스타·네이버 광고를 직접 돌리는데 같은 소재만 몇 달째 쓰는 쇼핑몰 — 광고를 돌린 뒤 숫자를 보내면 어떤 소재가 이겼는지 1쪽으로", 59000, 59000,
            [("기본 패키지", "이미지 4 + 숏폼 1 + 문구"), ("표준", "소재 10개 + 반응 비교 1회 · 119,000원"), ("작업 기간", "4일 (표준 6일)")]),
           ("06 · 세트", "상세페이지 첫 화면 + 숏폼 광고 세트", "svc-set.jpg", "첫 화면과 숏폼 세트 작업 예시 (SAMPLE · 가상 브랜드)",
            "광고를 보고 들어온 손님이 처음 보는 화면과 광고 영상을 같은 이야기로 맞추고 싶은 셀러 — 따로 맡기는 것보다 저렴", 59000, 59000,
            [("기본 패키지", "첫 화면 2안 + 10초 영상 1개"), ("작업 기간", "4일"), ("수정", "1회 (표준 2회)")])]
    rows = ""
    for no, name, img, alt, who, lp, op, facts in svc:
        fl = "".join(f'<li><span>{k}</span><b>{v}</b></li>' for k, v in facts)
        pr = (f'<p class="pr"><s>{lp:,}원</s> <em>{(lp - op) * 100 // lp}%</em> <strong>{op:,}원</strong> <small>기본 · 오픈 가격 첫 5건</small></p>' if lp > op
              else f'<p class="pr"><strong>{op:,}원</strong> <small>기본 가격부터</small></p>')
        rows += (f'<article class="svcrow"><img src="../img/home/{img}" alt="{alt}" width="720" height="540" loading="lazy">'
                 f'<div class="body"><span class="no">{no}</span><h2>{name}</h2><p class="who">{who}</p>'
                 f'{pr}'
                 f'<ul class="facts">{fl}</ul><span class="order">크몽에서 주문 · 승인 대기</span></div></article>\n')
    work = f"""<p class="meta"><span class="kicker">맡기기</span> · 사업자 · 브랜드 · 셀러</p>
<h1>작업 예시를 보고, <span class="mark">크몽에서 맡기세요</span></h1>
<p class="lead">AI로 빠르게 만들고, 납품 전 모든 줄과 그림은 사람이 직접 확인합니다. 결제와 정산은 크몽이 맡습니다.</p>
<p class="banner"><b>오픈 특가 · 서비스마다 첫 5건</b><span>그다음부터 줄 그은 정가로 받고, 가격은 앞으로도 계속 올릴 예정입니다.</span></p>
{rows}<p class="meta">모든 작업 예시는 가상 제품이며 SAMPLE 표시가 있습니다. 표준·고급 패키지와 정확한 수정 횟수는 크몽 상품 페이지에 있습니다.</p>
<h2>더 맡길 수 있는 일</h2>
<div class="next"><a href="repurpose/">영상 1편으로 한 달 SNS 채우기<span>쇼츠 3 · 카드뉴스 · 블로그 · SNS 글 4 · 129,000원부터 · 월 정액도</span></a><a href="english/">제품 영상, 해외 판매용 영어판으로<span>영어 자막 · 화면 글자 · 제목·설명 · 49,000원부터</span></a>
<a href="subscription/">AI 구독료, 한 달에 얼마 새는지 진단<span>계속 쓸 것·바꿀 것·끊을 것 1쪽 표 · 9,900원부터</span></a><a href="../tools/cost/">AI 구독료 계산기<span>체크만 하면 한 달·1년 합계 · 무료</span></a></div>
<h2>진행 순서</h2>
<ol class="steps4"><li><b>1 · 작업 예시 보고 주문</b><br>크몽에서. 제품 사진·이름·강조점 1~2개</li><li><b>2 · AI로 빠르게 초안</b><br>쓴 도구는 납품 때 적어 드림</li><li><b>3 · 사람이 한 줄씩 확인</b><br>성분 이름·제품 글자 대조</li><li><b>4 · 납품 · 수정</b><br>수정 횟수는 패키지대로</li></ol>
<div class="twobox"><div class="dark"><b>하지 않는 일</b><br>효능·1위·최초 같은 근거 없는 말 · 매출·성과 약속 · 다른 브랜드 페이지 따라 하기 · 의료기기·의약품·건강기능식품</div>
<div class="light"><b>문의</b><br>어떤 일인지, 대략 언제까지인지 두 가지만 적어 주세요. 비밀번호·로그인 정보는 어떤 경우에도 받지 않습니다.</div></div>
{INPOCK_BTN}"""
    os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
    open(os.path.join(ROOT, "work", "index.html"), "w", encoding="utf-8").write(
        page(f"맡기기: 작업 예시와 가격 | {SITE}", "세로 광고 영상·상세페이지 첫 화면 시안·카드뉴스·영문 상품 설명. 작업 예시와 오픈 가격(첫 5건)을 보고 크몽에서 맡기세요.",
             "work/", work, 1, jsonld={"@context": "https://schema.org", "@type": "WebPage", "name": "맡기기: 작업 예시와 가격", "inLanguage": "ko", "publisher": org},
             current="work", wide=True))
    urls.append(("work/", "2026-11-01"))

    # 영어 페이지(/en/) · 11-01 달러 시험 ①: 본문은 content/_en_*.part, 짝 한국어 페이지는 hreflang으로 연결
    for path, part, title, desc, key, ko, kind in EN_PAGES:
        body = open(os.path.join(ROOT, "content", part), encoding="utf-8").read()
        ld = {"@context": "https://schema.org", "@type": kind, "inLanguage": "en", "publisher": org}
        if kind == "Article":
            ld.update({"headline": title, "description": desc, "datePublished": "2026-10-31", "dateModified": "2026-11-01",
                       "author": org, "mainEntityOfPage": f"{BASE_URL}/{path}", "image": [f"{BASE_URL}/img/og.jpg"]})
            faq = re.findall(r'<section class="faq">(.*?)</section>', body, re.S)
            if faq:  # 본문에 실제로 있는 질문·답만
                qa = re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", faq[0], re.S)
                ld = {"@context": "https://schema.org", "@graph": [{k: v for k, v in ld.items() if k != "@context"}, {
                    "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": html.unescape(re.sub("<.*?>", "", q)),
                    "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re.sub("<.*?>", "", ans))}} for q, ans in qa]}]}
        else:
            ld["name"] = title
        os.makedirs(os.path.join(ROOT, path), exist_ok=True)
        open(os.path.join(ROOT, path, "index.html"), "w", encoding="utf-8").write(
            page(f"{title} | HEONLOG", desc, path, body, path.count("/"), og_type="article" if kind == "Article" else "website",
                 jsonld=ld, current=key, lang="en", alt=ko))
        urls.append((path, "2026-11-01"))

    nf = '<h1>페이지를 찾을 수 없습니다</h1><p>주소가 바뀌었거나 없는 글입니다. <a href="/">가이드 첫 화면</a>으로 가 주세요.</p>'
    open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(
        page(f"찾을 수 없음 | {SITE}", "없는 페이지입니다.", "404.html", nf, 0, notfound=True))

    sm = "\n".join(f"  <url><loc>{BASE_URL}/{p}</loc><lastmod>{d}</lastmod></url>" for p, d in urls)
    # /new/ = 가장 최근 「깃허브 털기」 글로 바로 보냄 (인포크 버튼 하나를 고정해 두고 글만 바뀌게 · 10-31)
    gh = [a for a in arts if a["slug"].startswith("github-")]
    if gh:
        latest = sorted(gh, key=lambda a: (a.get("date", ""), a["slug"]))[-1]
        url = f"{BASE_URL}/guide/{latest['slug']}/"
        os.makedirs(os.path.join(ROOT, "new"), exist_ok=True)
        open(os.path.join(ROOT, "new", "index.html"), "w", encoding="utf-8").write(
            f'<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><link rel="canonical" href="{url}">'
            f'<meta http-equiv="refresh" content="0; url={url}"><title>{html.escape(latest["title"])}</title>'
            f'<p><a href="{url}">{html.escape(latest["title"])}</a></p>')
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}\n</urlset>\n')
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n")
    print(f"글 {len(arts)}개 · 주소 {len(urls)}개 만듦")


if __name__ == "__main__":
    main()
