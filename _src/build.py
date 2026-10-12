#!/usr/bin/env python3
"""Build the VAS Ventures site.

    python3 _src/build.py

Edit pages in _src/pages/, the shared header/footer in _src/partials/,
styles in assets/site.css. Running this writes the final .html files to the
site root (index.html, about.html, …) and refreshes sitemap.xml.
Icons: write [[name]] (or [[name|extra-class]]) — files live in _src/icons/.
Founder photo: drop images/alok-trivedi.webp (or .jpg/.png) and rebuild.
"""
import json, os, re, time
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '_src')
SITE = 'https://vasventures.in'

PAGES = [
    # slug, nav group, <title>, description, breadcrumb name
    ('index', 'home', 'VAS Ventures | Parent company of Call-Astro, EyezonKid & Togethr',
     'VAS Ventures Pvt. Ltd. is a technology company from Noida, India, founded by Alok Trivedi — the parent company of Call-Astro, EyezonKid and Togethr.', 'Home'),
    ('about', 'about', 'About VAS Ventures | Our story, mission & values',
     'Learn about VAS Ventures Pvt. Ltd. — our story, mission, values and the brands we build: Call-Astro, EyezonKid and Togethr.', 'About'),
    ('alok-trivedi', 'about', 'Alok Trivedi | Founder of VAS Ventures',
     'Alok Trivedi is the founder of VAS Ventures Pvt. Ltd., the parent company of Call-Astro, EyezonKid and Togethr.', 'Alok Trivedi'),
    ('products', 'products', 'Our Products | Call-Astro, EyezonKid & Togethr — VAS Ventures',
     'Explore the products of VAS Ventures: Call-Astro for astrology and Vastu, EyezonKid for parental control and Togethr for community.', 'Products'),
    ('call-astro', 'products', 'Call-Astro | Online astrology & Vastu — a VAS Ventures product',
     'Call-Astro by VAS Ventures: chat with verified astrologers, free Kundli, matchmaking, horoscope, Vastu software, numerology and pooja booking.', 'Call-Astro'),
    ('eyezonkid', 'products', 'EyezonKid | Parental control — a VAS Ventures product',
     'EyezonKid by VAS Ventures: parental control for Mac, Windows, Android and iPhone with screen-time limits, app blocking and alerts — private chats stay private.', 'EyezonKid'),
    ('togethr', 'products', 'Togethr | Community app — a VAS Ventures product',
     'Togethr by VAS Ventures: a community app to connect, share and grow together, with secure OTP sign-in and full account control.', 'Togethr'),
    ('contact', 'contact', 'Contact VAS Ventures | Noida, India',
     'Contact VAS Ventures Pvt. Ltd. in Noida for business enquiries, partnerships, media and product support.', 'Contact'),
]
PRODUCT_PARENT = {'call-astro', 'eyezonkid', 'togethr'}
FOUNDER_PARENT = {'alok-trivedi'}

PRODUCTS = [
    ('call-astro', 'astro', 'om', 'Call-Astro', 'Astrology, Kundli, Vastu & spiritual services.'),
    ('eyezonkid', 'ezk', 'shield-halved', 'EyezonKid', 'Parental control for every screen.'),
    ('togethr', 'tog', 'users', 'Togethr', 'Community app with secure OTP sign-in.'),
]


def read(*p):
    with open(os.path.join(*p), encoding='utf-8') as f:
        return f.read()


def url(slug):
    return '/' if slug == 'index' else '/' + slug


def crumbs(slug, name):
    items = [('/', 'Home')]
    if slug in PRODUCT_PARENT:
        items.append(('/products', 'Products'))
    if slug in FOUNDER_PARENT:
        items.append(('/about', 'About'))
    li = ''.join(f'<li><a href="{h}">{n}</a></li>' for h, n in items)
    return f'<ol class="crumbs" aria-label="Breadcrumb">{li}<li aria-current="page">{name}</li></ol>'


def more(slug):
    cards = []
    for s, cls, ico, name, desc in PRODUCTS:
        if s == slug:
            continue
        cards.append(f'<a class="card rv" href="/{s}"><span class="pico pico--{cls}" style="width:54px;height:54px;border-radius:16px;margin-bottom:26px">[[{ico}]]</span>'
                     f'<h3>{name}</h3><p>{desc}</p><span class="link">Explore {name} [[arrow-right]]</span></a>')
    return ('<section class="sec sec--alt"><div class="wrap"><div class="head head--split">'
            '<div><span class="eyebrow rv">More from VAS Ventures</span><h2 class="h-lg rv rv-d1" style="margin-top:18px">Other products</h2></div>'
            '<p class="lead rv rv-d2">Every VAS Ventures brand is built to the same standards of quality, privacy and care.</p></div>'
            f'<div class="grid grid--2">{"".join(cards)}</div></div></section>')


def portrait():
    for ext in ('webp', 'jpg', 'jpeg', 'png'):
        if os.path.exists(os.path.join(ROOT, 'images', f'alok-trivedi.{ext}')):
            return f'<img src="/images/alok-trivedi.{ext}" alt="Alok Trivedi, Founder of VAS Ventures">'
    return '<span class="portrait__mono" aria-hidden="true">AT</span>'


def schema(slug, title, desc):
    org = {'@type': 'Organization', '@id': SITE + '/#org', 'name': 'VAS Ventures Pvt. Ltd.', 'alternateName': 'VAS Ventures',
           'url': SITE + '/', 'logo': SITE + '/images/VasVenturesLogo.png', 'email': 'info@vasventures.in', 'telephone': '+91-9650459807',
           'foundingDate': '2023-05-08', 'founder': {'@type': 'Person', '@id': SITE + '/alok-trivedi#person', 'name': 'Alok Trivedi'},
           'address': {'@type': 'PostalAddress', 'streetAddress': '417, Manhattan Street, Mahagun Moderne, Sector 78', 'addressLocality': 'Noida',
                       'addressRegion': 'Uttar Pradesh', 'postalCode': '201304', 'addressCountry': 'IN'},
           'subOrganization': [{'@type': 'Organization', 'name': 'Call-Astro', 'url': 'https://www.call-astro.com/'},
                               {'@type': 'Organization', 'name': 'EyezonKid', 'url': 'https://eyezonkid.com/'},
                               {'@type': 'Organization', 'name': 'Togethr', 'url': SITE + '/togethr'}]}
    graph = [org, {'@type': 'WebPage', 'url': SITE + url(slug), 'name': title, 'description': desc, 'publisher': {'@id': SITE + '/#org'}}]
    if slug == 'alok-trivedi':
        graph.append({'@type': 'Person', '@id': SITE + '/alok-trivedi#person', 'name': 'Alok Trivedi', 'jobTitle': 'Founder',
                      'worksFor': {'@id': SITE + '/#org'}, 'url': SITE + '/alok-trivedi'})
    return '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False) + '</script>'


def icons(html):
    used = []

    def rep(m):
        name, extra = m.group(1), (m.group(2) or '')
        if not os.path.exists(os.path.join(SRC, 'icons', name + '.svg')):
            raise SystemExit(f'Missing icon: {name}')
        if name not in used:
            used.append(name)
        cls = ('i ' + extra).strip()
        return f'<svg class="{cls}" aria-hidden="true"><use href="#i-{name}"/></svg>'

    html = re.sub(r'\[\[([a-z0-9-]+)(?:\|([a-z0-9- ]+))?\]\]', rep, html)
    syms = []
    for n in used:
        s = read(SRC, 'icons', n + '.svg')
        vb = re.search(r'viewBox="([^"]+)"', s).group(1)
        body = re.sub(r'(?s)^.*?<svg[^>]*>|</svg>\s*$', '', re.sub(r'<!--.*?-->', '', s)).strip()
        syms.append(f'<symbol id="i-{n}" viewBox="{vb}">{body}</symbol>')
    sprite = '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' + ''.join(syms) + '</svg>'
    return html.replace('{{sprite}}', sprite)


def main():
    v = str(int(time.time()))
    head, header, footer = read(SRC, 'partials', 'head.html'), read(SRC, 'partials', 'header.html'), read(SRC, 'partials', 'footer.html')
    for slug, nav, title, desc, name in PAGES:
        body = read(SRC, 'pages', slug + '.html')
        body = body.replace('{{crumbs}}', crumbs(slug, name)).replace('{{more}}', more(slug)).replace('{{portrait}}', portrait())
        hdr = header.replace(f'data-nav="{nav}"', f'data-nav="{nav}" aria-current="page"')
        h = (head.replace('{{title}}', title).replace('{{description}}', desc).replace('{{path}}', url(slug))
             .replace('{{schema}}', schema(slug, title, desc)))
        html = icons(h + hdr + body + footer).replace('{{v}}', v)
        with open(os.path.join(ROOT, slug + '.html'), 'w', encoding='utf-8') as f:
            f.write(html)
        print('✓', url(slug))
    today = date.today().isoformat()
    urls = [url(s) for s, *_ in PAGES] + ['/togethr-account']
    sm = ''.join(f'<url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod><priority>{"1.0" if u == "/" else "0.8"}</priority></url>' for u in urls)
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + sm + '</urlset>\n')
    print('✓ sitemap.xml')


if __name__ == '__main__':
    main()
