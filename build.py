#!/usr/bin/env python3
"""HEONLOG 안내 사이트 만들기. content/*.html(맨 위 --- 칸) → guide/<slug>/index.html + 첫 화면·소개·sitemap.
새 글: content/에 파일 하나 추가 → python3 build.py
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://heonlog.com"  # 주소가 정해지면 여기만 바꾼다 (끝에 / 없이)
SITE = "HEONLOG 가이드"
CTA = ('<aside class="cta" aria-label="무료 자료"><p><strong>광고 소재 체크리스트 무료 PDF</strong>. '
       '한 달 소재 개수, 모델컷·릴스 점검표, 화장품 광고 표현 주의점을 9쪽에 담았습니다. '
       '인스타그램 <a href="https://www.instagram.com/heonlog.studio/" rel="noopener">@heonlog.studio</a>로 DM 주시면 보내 드립니다.</p></aside>')


def read_articles():
    out = []
    for name in sorted(os.listdir(os.path.join(ROOT, "content"))):
        if not name.endswith(".html"):
            continue
        raw = open(os.path.join(ROOT, "content", name), encoding="utf-8").read()
        m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
        meta = dict(l.split(": ", 1) for l in m.group(1).splitlines() if ": " in l)
        meta["body"] = m.group(2)
        meta["slug"] = name[:-5].split("_", 1)[1]
        out.append(meta)
    return out


def page(title, desc, path, body, depth, og_image="img/og.jpg", og_type="website", jsonld=None, current=""):
    up = "../" * depth
    canon = f"{BASE_URL}/{path}"
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    nav = lambda href, label, key: f'<a href="{up}{href}"{" aria-current=\"page\"" if current == key else ""}>{label}</a>'
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta name="naver-site-verification" content="532f68a567a7bab22e3a75b82164f1a44f273f91">
<meta name="naver-site-verification" content="8a65c8d4b155d54f1e5790ab92ae384083104cec">
<meta name="google-site-verification" content="vj1r-xyzpSqau7A590A6hj5wXop7oyVEvwiRU8IKaeU">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{SITE}">
<meta property="og:locale" content="ko_KR">
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
</head>
<body>
<a class="skip" href="#main">본문 바로가기</a>
<header class="site"><div class="wrap">
<a class="logo" href="{up}index.html" aria-label="HEONLOG 가이드 첫 화면"><img src="{up}img/logo.svg" alt="HEONLOG" width="104" height="26"></a>
<nav class="top" aria-label="주 메뉴">{nav("index.html", "가이드", "home")}{nav("about/index.html", "소개", "about")}</nav>
</div></header>
<main id="main"><div class="wrap">
{body}
</div></main>
<footer class="site"><div class="wrap">
<p>HEONLOG · AI로 일하는 1인 회사 · 문의 인스타그램 <a href="https://www.instagram.com/heonlog.studio/" rel="noopener">@heonlog.studio</a></p>
<p>글 속 법·제도 내용은 정리일 뿐 법률 자문이 아닙니다. 게시 전 공식 출처의 최신 내용을 확인하세요. · <a href="{up}about/index.html#privacy">개인정보·이용 안내</a></p>
</div></footer>
</body>
</html>
"""


def main():
    arts = read_articles()
    org = {"@type": "Organization", "name": "HEONLOG", "url": BASE_URL + "/",
           "sameAs": ["https://www.instagram.com/heonlog.studio/"]}
    urls = [("", "2026-10-30"), ("about/", "2026-10-30")]
    for a in arts:
        path = f"guide/{a['slug']}/"
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"],
              "description": a["description"], "datePublished": a["date"], "dateModified": a["date"],
              "inLanguage": "ko", "image": [f"{BASE_URL}/{a.get('image', 'img/og.jpg')}"],
              "author": org, "publisher": org, "mainEntityOfPage": f"{BASE_URL}/{path}",
              "keywords": a["keyword"]}
        body = (f'<article><p class="meta"><span class="kicker">{html.escape(a["kicker"])}</span> · '
                f'{a["date"].replace("-", ".")} · HEONLOG</p>\n<h1>{html.escape(a["title"])}</h1>\n'
                + a["body"].replace("{{up}}", "../../") + "\n" + CTA + "</article>")
        os.makedirs(os.path.join(ROOT, path), exist_ok=True)
        open(os.path.join(ROOT, path, "index.html"), "w", encoding="utf-8").write(
            page(f'{a["title"]} | {SITE}', a["description"], path, body, 2,
                 og_image=a.get("image", "img/og.jpg"), og_type="article", jsonld=ld))
        urls.append((path, a["date"]))

    items = "\n".join(
        f'<li><a href="guide/{a["slug"]}/index.html">{html.escape(a["title"])}</a><p>{html.escape(a["description"])}</p></li>'
        for a in arts)
    home = f"""<p class="meta"><span class="kicker">작은 뷰티 브랜드용</span></p>
<h1>광고 소재를 직접 만드는 브랜드를 위한 <span class="mark">실무 가이드</span></h1>
<p class="lead">제품 사진, AI 모델컷, 상세페이지 문구, 광고 표시 규정. HEONLOG가 직접 만들어 보고 공식 자료로 확인한 것만 정리합니다. 확인하지 못한 내용은 「미확인」으로 적습니다.</p>
<h2>가이드</h2>
<ul class="list">
{items}
</ul>
{CTA}"""
    site_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": BASE_URL + "/",
               "inLanguage": "ko", "publisher": org}
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(
        page(f"{SITE} · 작은 뷰티 브랜드의 광고 소재·AI 모델컷 실무",
             "작은 뷰티 브랜드가 광고 소재를 직접 만들 때 필요한 것: AI 모델컷 만드는 법, 제품 사진 AI 프롬프트, 화장품 광고 금지 표현, 가상인물 표시, 상세페이지 자문. 직접 해 본 것과 공식 출처만.",
             "", home, 0, jsonld=site_ld, current="home"))

    about = open(os.path.join(ROOT, "content", "_about.part"), encoding="utf-8").read()
    os.makedirs(os.path.join(ROOT, "about"), exist_ok=True)
    open(os.path.join(ROOT, "about", "index.html"), "w", encoding="utf-8").write(
        page(f"소개: AI로 일하는 1인 회사 HEONLOG | {SITE}",
             "HEONLOG는 AI로 제품 화보·모델컷·짧은 광고 영상을 만드는 1인 회사입니다. 이 사이트에는 직접 해 본 것과 공식 출처로 확인한 것만 씁니다.",
             "about/", about + CTA, 1, jsonld={"@context": "https://schema.org", "@type": "AboutPage", "name": "HEONLOG 소개", "publisher": org},
             current="about"))

    nf = '<h1>페이지를 찾을 수 없습니다</h1><p>주소가 바뀌었거나 없는 글입니다. <a href="/">가이드 첫 화면</a>으로 가 주세요.</p>'
    open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(
        page(f"찾을 수 없음 | {SITE}", "없는 페이지입니다.", "404.html", nf, 0).replace(
            '<meta name="description"', '<meta name="robots" content="noindex">\n<meta name="description"'))

    sm = "\n".join(f"  <url><loc>{BASE_URL}/{p}</loc><lastmod>{d}</lastmod></url>" for p, d in urls)
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}\n</urlset>\n')
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n")
    print(f"글 {len(arts)}개 · 주소 {len(urls)}개 만듦")


if __name__ == "__main__":
    main()
