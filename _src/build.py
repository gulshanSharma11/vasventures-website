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
     'Alok Trivedi — Founder & Director of VAS Ventures Pvt. Ltd., Jyotirvid and Vastu Visharad with 18+ years in Jyotish, Vastu Shastra and Numerology.', 'Alok Trivedi'),
    ('products', 'products', 'Our Products | Call-Astro, EyezonKid & Togethr — VAS Ventures',
     'Explore the products of VAS Ventures: Call-Astro for astrology and Vastu, EyezonKid for parental control and Togethr, an astrology-powered social app.', 'Products'),
    ('call-astro', 'products', 'Call-Astro | Online astrology & Vastu — a VAS Ventures product',
     'Call-Astro by VAS Ventures: chat with verified astrologers, free Kundli, matchmaking, horoscope, Vastu software, numerology and pooja booking.', 'Call-Astro'),
    ('eyezonkid', 'products', 'EyezonKid | Parental control — a VAS Ventures product',
     'EyezonKid by VAS Ventures: parental control for Mac, Windows, Android and iPhone with screen-time limits, app blocking and alerts — private chats stay private.', 'EyezonKid'),
    ('togethr', 'products', 'Togethr | Astrology & numerology social app — a VAS Ventures product',
     'Togethr by VAS Ventures: find friends and matches with astrology, numerology and soul bond compatibility. Daily cosmic guidance and community chat.', 'Togethr'),
    ('apps', 'products', 'Our Apps on Google Play | VAS Ventures',
     'All apps by VAS Ventures Pvt. Ltd. on Google Play: Call Astro, Call-Astro Partner, CA Vastu, CA Astrology, CA Numerology, CA Tarot, EyezonKid and Togethr.', 'Apps'),
    ('contact', 'contact', 'Contact VAS Ventures | Noida, India',
     'Contact VAS Ventures Pvt. Ltd. in Noida for business enquiries, partnerships, media and product support.', 'Contact'),
]
PRODUCT_PARENT = {'call-astro', 'eyezonkid', 'togethr', 'apps'}
FOUNDER_PARENT = {'alok-trivedi'}

PLAY = 'https://play.google.com/store/apps/details?id='
PLAY_DEV = 'https://play.google.com/store/apps/developer?id=Vas+Venture+Pvt+Ltd'
# slug, group, name, package, category, audience, description, play-lh icon id
APPS = [
    ('call-astro', 'astro', 'Call Astro: Talk to Astrologer', 'com.callastrouser', 'Lifestyle', 'For users',
     'Chat live with verified astrologers — your first chat is free. Free Kundli, horoscope matching and daily Panchang.',
     'vyEG9egs4Dk16WDT35pp9IgPNLx5PScThnxJdZFSyVop5xWacFQ30zcGl91Uk3LmjfvwcVOJqJgAfofQqKoQ'),
    ('call-astro-partner', 'astro', 'Call-Astro Partner', 'com.callastro', 'Business', 'For astrologers',
     'Join the Call-Astro panel: go live, set your call rates, track every call and see your daily earnings.',
     'TVcRg8us6KXoyDYQ9U0nHO8UMv_0FvYJrWMh6piOTjwETD4kX_JLY7JqD-v5Wmhikj1uqea8RaBbzB3ETBvI'),
    ('ca-vastu', 'astro', 'CA Vastu: Compass & Floor Plan', 'com.vas_ventures.vastu', 'Education', 'For homes & professionals',
     'Vastu compass, 8 and 16-zone grids on any floor plan, Brahmasthan detection, dosha checks and PDF reports.',
     'cRc1Jnw2ThMoZE204MD-PWA-S6Q6eLhq9Uqd8epFdN4JZUlIhwxPz1m_VCazdGRiEBQC_H36d0sqSORJdt4gQA'),
    ('ca-astrology', 'astro', 'CA Astrology', 'com.vasVentures.astrology.ca_astrology', 'Education', 'For users',
     'Daily horoscope, detailed Kundli insights and guidance on life, relationships and career.',
     '0zqG-2wqg7ZYSTJpOH7URNhFHxujKlsTWjuLK5lF8kydaWcqV_NnwD-hkPvK8sm-hO92tSaGbE9TSMTWxK78'),
    ('ca-numerology', 'astro', 'CA Numerology', 'com.callAstro.numerologyApp', 'Lifestyle', 'For users',
     'Personal numerology reports — Moolank, Bhagyank and name-number analysis with Pythagorean and Chaldean methods.',
     'upHPaxB1aTMZmJr8sAA8Ig7kSjZosUAMjmLtE_cV9tLdpD6w1XeN2VNJXBQt2LgNjNh7iON4Z5QhWi0o6WxVxg'),
    ('ca-tarot', 'astro', 'CA Tarot', 'com.callastro.tarot_app', 'Lifestyle', 'For users',
     'Pick and reveal tarot cards, get a Card of the Day, and read upright and reversed meanings in Hindi and English.',
     'r-f0fzXDCpLsib7zoCclP6rZX3VCwQemgYKedgZeR1k6ekWq7bPVBRm4L-KK53xDJ18kazCudSTBbMhIZBFk5w'),
    ('eyezonkid', 'ezk', 'EyezonKid: Parental Control', 'com.vasventures.eyezonkid', 'Parenting', 'For parents',
     'Daily screen-time limits, app blocking, bedtime and study schedules, activity reports and uninstall protection.',
     'aSsv9VL7Y7aciSW9koMQ2r2oWdZklbnJrJ7RY1e_U5QFRIqjCvtv04M0FXqmbP5gqESDTPOyBoeoQlo3FtdQXg'),
    ('togethr', 'tog', 'Togethr', 'com.vas_ventures.togethr', 'Social', 'For connections',
     'Find friends and matches through astrology, numerology and soul bond compatibility, with daily cosmic guidance.',
     'Zl-dDUiIWXmggsVHZhqUCkVC0hEdOiL2aLua4mU5H8g7HaSXefNIaTaEpFFYCiC90JlF2yRfgph23wGDrX-nH0Y'),
]
APP = {a[0]: a for a in APPS}


def app_icon(slug, cls='appicon'):
    a = APP[slug]
    for ext in ('webp', 'png', 'jpg'):  # a saved copy in images/apps/ wins over the Play Store image
        if os.path.exists(os.path.join(ROOT, 'images', 'apps', f'{slug}.{ext}')):
            src = f'/images/apps/{slug}.{ext}'; break
    else:
        src = f'https://play-lh.googleusercontent.com/{a[7]}=w192-h192'
    lazy = '' if 'lg' in cls else ' loading="lazy"'
    return f'<img class="{cls}" src="{src}" width="96" height="96" alt="{a[2]} app icon"{lazy}>'


def play_btn(slug, extra=''):
    return (f'<a class="btn btn--play {extra}" href="{PLAY}{APP[slug][3]}" target="_blank" rel="noopener">'
            '[[google-play]]<span><small>GET IT ON</small>Google Play</span></a>')


def apps_grid(group):
    out = []
    for slug, g, name, pkg, cat, aud, desc, _ in APPS:
        if group != 'all' and g != group:
            continue
        out.append(f'<article class="app rv">{app_icon(slug)}<div class="app__body"><div class="app__tags"><span>{cat}</span><span>{aud}</span></div>'
                   f'<h3>{name}</h3><p>{desc}</p><a class="link" href="{PLAY}{pkg}" target="_blank" rel="noopener">[[google-play]]View on Google Play [[up-right]]</a></div></article>')
    one = ' apps--one' if len(out) == 1 else ''
    return f'<div class="apps{one}">{"".join(out)}</div>'


def mini_apps(group):
    items = ''.join(f'<a class="mini" href="{PLAY}{a[3]}" target="_blank" rel="noopener" title="{a[2]}">{app_icon(a[0], "appicon appicon--xs")}<span>{a[2].split(":")[0]}</span></a>'
                    for a in APPS if a[1] == group)
    n = sum(1 for a in APPS if a[1] == group)
    return f'<div class="minis"><small>{n} apps on Google Play</small><div class="minis__row">{items}</div></div>'


def apps_strip():
    icons = ''.join(f'<a class="apps-strip__i" href="{PLAY}{a[3]}" target="_blank" rel="noopener" title="{a[2]}">{app_icon(a[0], "appicon appicon--sm")}</a>' for a in APPS)
    return icons


PRODUCTS = [
    ('call-astro', 'astro', 'om', 'Call-Astro', 'Astrology, Kundli, Vastu & spiritual services.'),
    ('eyezonkid', 'ezk', 'shield-halved', 'EyezonKid', 'Parental control for every screen.'),
    ('togethr', 'tog', 'users', 'Togethr', 'Friends and matches through astrology, numerology and soul bond compatibility.'),
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
            return f'<img src="/images/alok-trivedi.{ext}" width="1000" height="1683" alt="Alok Trivedi, Founder &amp; Director of VAS Ventures">'
    return '<span class="portrait__mono" aria-hidden="true">AT</span>'


def avatar():
    for ext in ('webp', 'jpg', 'png'):
        if os.path.exists(os.path.join(ROOT, 'images', f'alok-trivedi-avatar.{ext}')):
            return f'<img class="sign__av" src="/images/alok-trivedi-avatar.{ext}" width="104" height="104" alt="" loading="lazy">'
    return '<span class="sign__av">AT</span>'


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
        graph.append({'@type': 'Person', '@id': SITE + '/alok-trivedi#person', 'name': 'Alok Trivedi', 'jobTitle': 'Founder & Director', 'image': SITE + '/images/alok-trivedi.webp',
                      'knowsAbout': ['Vedic astrology', 'Vastu Shastra', 'Numerology'],
                      'memberOf': {'@type': 'Organization', 'name': 'Indian Council of Astrological Sciences'},
                      'sameAs': ['https://tripadajyotish.com/about-alok-trivedi/'],
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
        body = re.sub(r'\{\{apps:([a-z]+)\}\}', lambda m: apps_grid(m.group(1)), body)
        body = re.sub(r'\{\{miniapps:([a-z]+)\}\}', lambda m: mini_apps(m.group(1)), body)
        body = re.sub(r'\{\{play:([a-z-]+)\}\}', lambda m: play_btn(m.group(1)), body)
        body = re.sub(r'\{\{icon:([a-z-]+)\}\}', lambda m: app_icon(m.group(1), 'appicon appicon--lg'), body)
        body = body.replace('{{appstrip}}', apps_strip()).replace('{{appcount}}', str(len(APPS))).replace('https://play.google.com/store/apps/dev?id=VAS+Ventures', PLAY_DEV)
        body = body.replace('{{crumbs}}', crumbs(slug, name)).replace('{{more}}', more(slug)).replace('{{portrait}}', portrait()).replace('{{avatar}}', avatar())
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
