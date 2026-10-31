#!/usr/bin/env python3
"""HEONLOG 안내 사이트 만들기. content/*.html(맨 위 --- 칸) → guide/<slug>/index.html + 첫 화면·소개·sitemap.
새 글: content/에 파일 하나 추가 → python3 build.py
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://heonlog.com"  # 주소가 정해지면 여기만 바꾼다 (끝에 / 없이)
SITE = "HEONLOG 가이드"
CTA = ''  # 대표님 10-30: 「~보내 주시면 드립니다」 같은 주는 약속 문구 넣지 않음
# 10-31: 주는 약속 없이 길 안내만 · 11-01: 「소식받기」(인포크 기능과 헷갈림) 빼고 인스타 한 줄로 — 첫 화면·/free/ 끝
NEXT = ('<aside class="cta" aria-label="다음 회"><p><strong>다음 깃허브 털기도 보고 싶다면</strong> · '
        '다음 회차는 인스타그램 <a href="https://www.instagram.com/heonlog.studio/" rel="noopener">@heonlog.studio</a>에 먼저 올라옵니다.</p></aside>')
# 11-01 무료·유료 경계 보고서 4절 A(정리본 판매 전 판): 가이드 끝 3층 안내 — 아직 없는 링크·결제 버튼·신청서는 만들지 않음.
# 정리본 판매 시작(11-08 예정) 때 셋째 줄에 링크, 신청서 연 날(11-15~) 둘째 줄에 신청 링크를 붙인다.
GUIDE_NEXT = ('<aside class="cta tiers" aria-label="더 해 보고 싶다면"><p><strong>이 회차를 내 컴퓨터에서 똑같이 해 보고 싶다면</strong></p>\n<ul>\n'
              '<li><b>이 글 · 무료</b> — 무엇을 하는 도구인지, 해 보니 어땠는지, 어디가 함정인지까지 적었습니다.</li>\n'
              '<li><b>깔기 전 시작 키트 · 무료 이메일 신청</b> — 어느 깃허브 도구든 깔기 전에 확인할 체크리스트와 AI에게 먼저 묻는 문장 1개. 신청서는 준비 중입니다.</li>\n'
              '<li><b>깃허브 털기 정리본 · 3,900원</b> — AI에게 실제로 붙여 넣은 문장과 막혔을 때 물은 문장을 회차별로 묶고 있습니다. 2026년 11월 8일 판매 시작 예정이며, 시작하면 이 자리에 링크를 붙입니다.</li>\n'
              '</ul>\n<p>다음 회차는 인스타그램 <a href="https://www.instagram.com/heonlog.studio/" rel="noopener">@heonlog.studio</a>에 먼저 올라옵니다.</p></aside>')
# 예전 뷰티 글: 지우거나 숨기지 않고(주소·사이트맵 그대로) 글 맨 위에 「예전 글」 표시만 · 11-01
OLD_NOTE = ('<p class="notice oldnote"><strong>예전 글</strong> · 2026년 10월, 작은 뷰티 브랜드 광고 소재를 만들 때 정리한 글입니다. '
            '법·제도 내용은 쓴 날짜 기준이니 최신 원문으로 다시 확인하세요. 지금 HEONLOG는 <a href="../../index.html">「깃허브 털기」</a>를 연재합니다. 이 주제(제품 화보·모델컷·상세페이지·광고 문구 점검)로 작업을 맡기고 싶다면 <a href="../../work/">맡기기</a>를 봐 주세요.</p>\n')


# 맡기기 문의 = 인포크 「비즈니스 제안」 하나로 (이메일 주소는 페이지에 쓰지 않음 · 11-01)
INPOCK_BTN = ('<p class="ask"><a class="btn" href="https://link.inpock.co.kr/heonlog" rel="noopener">인포크 「비즈니스 제안」으로 문의하기</a>'
              '<span>링크 페이지의 「비즈니스 제안」 버튼에서 남길 수 있습니다. 결제는 이 사이트에서 받지 않습니다.</span></p>')
# (주소, 본문 파일, 제목, 설명, 메뉴 칸)
WORK_PAGES = [
    ("work/", "_work.part", "맡기기: HEONLOG에 맡길 수 있는 작은 일",
     "AI 구독비 진단, 영상 1편을 글 7조각으로, 한국 상품·영상을 영어로. 직접 해 본 방식 그대로 맡아 하는 작은 일과 시범 가격입니다.", "work"),
    ("work/subscription/", "_work_subscription.part", "AI 구독비 다이어트 30분 진단",
     "지금 쓰는 유료 AI·디자인 구독 목록을 계속 쓸 것·싼 요금제·무료 대안·안 써도 되는 것으로 나눈 1쪽 표와 30분 화상 설명. 시범 가격 19,000원.", "work"),
    ("work/repurpose/", "_work_repurpose.part", "영상 1편을 글 7조각으로: 월 정액",
     "유튜브 영상 한 편을 스레드·링크드인·블로그 글 등 7조각 초안으로 바꿉니다. 실제로 영상 한 편에서 나온 7조각 견본과 시범 가격 월 99,000원.", "work"),
    ("work/english/", "_work_english.part", "한국 상품·영상을 영어로",
     "한국 소형 유튜버 영상의 영어 자막·제목·설명, 해외 K-뷰티 셀러용 영어 상품 설명. 직접 번역한 영어 견본 1쪽과 시범 가격.", "work"),
    ("tools/cost/", "_tools_cost.part", "AI 구독료 계산기",
     "쓰는 AI 구독에 체크하면 한 달·1년 합계가 나옵니다. 요금은 공식 요금 페이지에서 확인한 것만, 확인 날짜와 함께 넣었습니다. 저장·쿠키 없음.", ""),
]

# 영어 페이지 (주소, 본문 파일, 제목, 설명, 메뉴 칸, 짝 한국어 주소 또는 None, schema 종류) · 11-01
EN_PAGES = [
    ("en/", "_en_home.part", "Free GitHub tools, installed and rated by a non-developer",
     "I have AI install free GitHub tools instead of paid ones, then rate install difficulty (click only to gave up), what broke, and the catch.",
     "home", "", "WebPage"),
    ("en/guide/archify/", "_en_guide_archify.part", "GitHub Teardown #01 · archify: turn a hard-to-explain workflow into one picture",
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
         lang="ko", alt=None):
    """lang="en" = 영어 페이지(메뉴·아래줄 영어) · alt = 짝 언어 페이지 주소(hreflang·「한국어」/「EN」 링크) · 11-01"""
    up = "../" * depth
    canon = f"{BASE_URL}/{path}"
    hl = ""
    if alt is not None:
        ko_p, en_p = (path, alt) if lang == "ko" else (alt, path)
        hl = (f'<link rel="alternate" hreflang="ko" href="{BASE_URL}/{ko_p}">\n'
              f'<link rel="alternate" hreflang="en" href="{BASE_URL}/{en_p}">\n'
              f'<link rel="alternate" hreflang="x-default" href="{BASE_URL}/{ko_p}">\n')
    other = up + (alt if alt is not None else ("en/" if lang == "ko" else "")) + "index.html"
    nav = lambda href, label, key, extra="": f'<a href="{up}{href}"{" aria-current=\"page\"" if current == key else ""}{extra}>{label}</a>'
    if lang == "en":
        top = (f'<a class="skip" href="#main">Skip to content</a>\n<header class="site"><div class="wrap">\n'
               f'<a class="logo" href="{up}en/index.html" aria-label="HEONLOG home (English)"><img src="{up}img/logo.svg" alt="HEONLOG" width="104" height="26"></a>\n'
               f'<nav class="top" aria-label="Main menu">{nav("en/index.html", "Guides", "home")}{nav("en/free/index.html", "Free preview", "free")}'
               f'{nav("en/work/english-product-copy/index.html", "Hire", "work")}'
               f'<a class="lang" href="{other}" lang="ko" hreflang="ko">한국어</a></nav>\n</div></header>')
        foot = (f'<footer class="site"><div class="wrap">\n<p>HEONLOG · GitHub tools, installed by a non-developer · Instagram '
                f'<a href="https://www.instagram.com/heonlog.studio/" rel="noopener">@heonlog.studio</a> (in Korean) · Business inquiries: the '
                f'&ldquo;Business proposal&rdquo; button on my <a href="https://link.inpock.co.kr/heonlog" rel="noopener">link page</a></p>\n'
                f'<p>Nothing here is legal advice. Check the official sources before you rely on it. · '
                f'<a href="{up}about/index.html#privacy" lang="ko" hreflang="ko">Privacy &amp; terms (Korean)</a> · '
                f'<a href="{other}" lang="ko" hreflang="ko">한국어</a></p>\n</div></footer>')
    else:
        top = (f'<a class="skip" href="#main">본문 바로가기</a>\n<header class="site"><div class="wrap">\n'
               f'<a class="logo" href="{up}index.html" aria-label="HEONLOG 가이드 첫 화면"><img src="{up}img/logo.svg" alt="HEONLOG" width="104" height="26"></a>\n'
               f'<nav class="top" aria-label="주 메뉴">{nav("index.html", "가이드", "home")}{nav("free/index.html", "무료 맛보기", "free")}'
               f'{nav("work/index.html", "맡기기", "work")}{nav("about/index.html", "소개", "about")}'
               f'<a class="lang" href="{other}" lang="en" hreflang="en" aria-label="English">EN</a></nav>\n</div></header>')
        foot = (f'<footer class="site"><div class="wrap">\n<p>HEONLOG · 개발 몰라도 깃허브 털기 · 인스타그램 '
                f'<a href="https://www.instagram.com/heonlog.studio/" rel="noopener">@heonlog.studio</a> · 문의·협찬 제안은 '
                f'<a href="https://link.inpock.co.kr/heonlog" rel="noopener">링크 페이지</a>의 「비즈니스 제안」 · '
                f'<a href="{other}" lang="en" hreflang="en">English</a></p>\n'
                f'<p>글 속 법·제도 내용은 정리일 뿐 법률 자문이 아닙니다. 게시 전 공식 출처의 최신 내용을 확인하세요. · '
                f'<a href="{up}about/index.html#privacy">개인정보·이용 안내</a></p>\n</div></footer>')
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta name="naver-site-verification" content="532f68a567a7bab22e3a75b82164f1a44f273f91">
<meta name="naver-site-verification" content="8a65c8d4b155d54f1e5790ab92ae384083104cec">
<meta name="google-site-verification" content="vj1r-xyzpSqau7A590A6hj5wXop7oyVEvwiRU8IKaeU">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
{hl}<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{"HEONLOG" if lang == "en" else SITE}">
<meta property="og:locale" content="{"en_US" if lang == "en" else "ko_KR"}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE_URL}/{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="{up}img/favicon.png">
<link rel="apple-touch-icon" href="{up}img/icon-180.png">
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="stylesheet" href="{up}style.css">
{ld}
<!-- Cloudflare Web Analytics (쿠키 없는 방문 수 · 11-01) --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "9f4bf7e4514c4afc99a713798af12a04"}}'></script><!-- End Cloudflare Web Analytics -->
</head>
<body>
{top}
<main id="main"><div class="wrap">
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
    urls = [("", "2026-10-30"), ("about/", "2026-10-30"), ("free/", "2026-11-01")]
    for a in arts:
        path = f"guide/{a['slug']}/"
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"],
              "description": a["description"], "datePublished": a["date"], "dateModified": a["date"],
              "inLanguage": "ko", "image": [f"{BASE_URL}/{a.get('image', 'img/og.jpg')}"],
              "author": org, "publisher": org, "mainEntityOfPage": f"{BASE_URL}/{path}",
              "keywords": a["keyword"]}
        body = (f'<article><p class="meta"><span class="kicker">{html.escape(a["kicker"])}</span> · '
                f'{a["date"].replace("-", ".")} · HEONLOG</p>\n<h1>{html.escape(a["title"])}</h1>\n'
                + ("" if a["slug"].startswith("github-") else OLD_NOTE)
                + a["body"].replace("{{up}}", "../../") + "\n" + (GUIDE_NEXT if a["slug"].startswith("github-") else CTA) + "</article>")
        os.makedirs(os.path.join(ROOT, path), exist_ok=True)
        open(os.path.join(ROOT, path, "index.html"), "w", encoding="utf-8").write(
            page(f'{a["title"]} | {SITE}', a["description"], path, body, 2,
                 og_image=a.get("image", "img/og.jpg"), og_type="article", jsonld=ld, alt=EN_ALT.get(path)))
        urls.append((path, a["date"]))

    li = lambda a: f'<li><a href="guide/{a["slug"]}/index.html">{html.escape(a["title"])}</a><p>{html.escape(a["description"])}</p></li>'
    gh = sorted([a for a in arts if a["slug"].startswith("github-")], key=lambda a: (a.get("date", ""), a["slug"]), reverse=True)
    old = [a for a in arts if not a["slug"].startswith("github-")]
    home = f"""<p class="meta"><span class="kicker">개발 몰라도 깃허브 털기</span></p>
<h1>유료 대신 무료 도구, <span class="mark">직접 깔아 보고</span> 알려 드려요</h1>
<p class="lead">깃허브에 있는 무료 도구를 개발 모르는 사람이 AI한테 시켜 직접 깔아 보고, 설치 난이도(⭐ 클릭만 · ⭐⭐ 따라 하면 됨 · ⭐⭐⭐ 터미널 필요 · 💀 포기)와 막힌 곳까지 그대로 적습니다. 깔아 보지 않은 것은 쓰지 않습니다.</p>
<p class="golink"><a href="free/index.html">월 구독 도구 대신 쓸 수 있는 깃허브 무료 대안 맛보기 →</a></p>
<h2>깃허브 털기</h2>
<ul class="list">
{chr(10).join(li(a) for a in gh)}
</ul>
{NEXT}
<details class="oldposts"><summary>예전 글 {len(old)}편 · 작은 뷰티 브랜드 광고 소재</summary>
<ul class="list">
{chr(10).join(li(a) for a in old)}
</ul>
</details>"""
    site_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": BASE_URL + "/",
               "inLanguage": "ko", "publisher": org}
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(
        page(f"{SITE} · 개발 몰라도 깃허브 털기",
             "유료 대신 쓸 수 있는 깃허브 무료 도구를 개발 모르는 사람이 직접 깔아 보고 설치 난이도·막힌 곳·함정까지 정리합니다. 직접 깔아 본 것만 씁니다.",
             "", home, 0, jsonld=site_ld, current="home", alt="en/"))

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
        "{{guides}}", "\n".join(f'<li><a href="../guide/{a["slug"]}/index.html">{html.escape(a["title"])}</a></li>'
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

    # 영어 페이지(/en/) · 11-01 달러 시험 ①: 본문은 content/_en_*.part, 짝 한국어 페이지는 hreflang으로 연결
    for path, part, title, desc, key, ko, kind in EN_PAGES:
        body = open(os.path.join(ROOT, "content", part), encoding="utf-8").read()
        ld = {"@context": "https://schema.org", "@type": kind, "inLanguage": "en", "publisher": org}
        if kind == "Article":
            ld.update({"headline": title, "description": desc, "datePublished": "2026-10-31", "dateModified": "2026-11-01",
                       "author": org, "mainEntityOfPage": f"{BASE_URL}/{path}", "image": [f"{BASE_URL}/img/og.jpg"]})
        else:
            ld["name"] = title
        os.makedirs(os.path.join(ROOT, path), exist_ok=True)
        open(os.path.join(ROOT, path, "index.html"), "w", encoding="utf-8").write(
            page(f"{title} | HEONLOG", desc, path, body, path.count("/"), og_type="article" if kind == "Article" else "website",
                 jsonld=ld, current=key, lang="en", alt=ko))
        urls.append((path, "2026-11-01"))

    nf = '<h1>페이지를 찾을 수 없습니다</h1><p>주소가 바뀌었거나 없는 글입니다. <a href="/">가이드 첫 화면</a>으로 가 주세요.</p>'
    open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(
        page(f"찾을 수 없음 | {SITE}", "없는 페이지입니다.", "404.html", nf, 0).replace(
            '<meta name="description"', '<meta name="robots" content="noindex">\n<meta name="description"'))

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
