#!/usr/bin/env python3
"""Copia il sito riservato agli agenti "MAK eBook Agente" (Google Site) in Siti/EBOOK/:
pagine in pagine/ come Markdown, immagini in immagini/, collegamenti in collegamenti.csv.

Il sito richiede il login Google. Lo script NON fa login e non vede password: si aggancia a un
Chrome già aperto, in cui il login l'hai fatto tu. Apri quel Chrome con:

    Mac:      Siti/_script/avvia_chrome_ebook.sh
    Windows:  powershell -ExecutionPolicy Bypass -File Siti\\_script\\avvia_chrome_ebook.ps1

poi, quando vedi la home del sito agenti:

    .venv/bin/python Siti/_script/ebook_pagine.py              (Mac)
    .venv\\Scripts\\python Siti\\_script\\ebook_pagine.py      (Windows)

Dopo le pagine si scaricano i file collegati con ebook_file.py.
MATERIALE RISERVATO AGLI AGENTI MAK: resta su questo computer, mai su GitHub.
Richiede playwright (nel .venv del workspace) e pandoc."""
import argparse, csv, hashlib, http.cookiejar, json, os, re, subprocess, sys, time, urllib.parse, urllib.request

from playwright.sync_api import sync_playwright

BASE = "https://sites.google.com/view/makebookagente"
CDP = "http://127.0.0.1:9333"
ATTESA_LOGIN = 40 * 60  # secondi
QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.join(QUI, "..", "EBOOK")
PAGINE = os.path.join(RADICE, "pagine")
IMMAGINI = os.path.join(RADICE, "immagini")
GREZZI = os.environ.get("EBOOK_GREZZI")  # cartella facoltativa per l'HTML originale

# raccoglie contenuto, link, incorporamenti e immagini della pagina corrente
ESTRAI = r"""() => {
  // in Google Sites il contenuto sta nelle <section>; role="main" marca solo il primo blocco di testo
  const sez = [...document.querySelectorAll('section')];
  const main = {contains: e => sez.some(s => s.contains(e)),
                querySelectorAll: q => sez.flatMap(s => [...s.querySelectorAll(q)]),
                outerHTML: sez.map(s => s.outerHTML).join('\n')};
  const ass = u => { try {
    const a = new URL(u, location.href);
    // i link esterni passano da google.com/url?q=...: tengo la destinazione vera
    return /(^|\.)google\.com$/.test(a.hostname) && a.pathname === '/url' && a.searchParams.get('q') ? a.searchParams.get('q') : a.href;
  } catch (e) { return '' } };
  const link = [...document.querySelectorAll('a[href]')].map(a => ({
    url: ass(a.getAttribute('href')), testo: (a.innerText || a.getAttribute('aria-label') || '').trim(),
    nav: !main.contains(a)}));
  const embed = [];
  main.querySelectorAll('iframe, [data-url], [data-embed-open-url], [data-embed-doc-id], [data-src]').forEach(e => {
    for (const k of ['src', 'data-src', 'data-url', 'data-embed-open-url', 'data-embed-download-url']) {
      const v = e.getAttribute(k); if (v && !v.startsWith('about:')) embed.push({url: ass(v), testo: e.getAttribute('aria-label') || e.title || k});
    }
    const id = e.getAttribute('data-embed-doc-id');
    if (id) embed.push({url: 'https://drive.google.com/open?id=' + id, testo: e.getAttribute('aria-label') || 'drive'});
  });
  const img = main.querySelectorAll('img').map(i => ({url: i.currentSrc || i.src, alt: i.alt || '', w: i.naturalWidth, h: i.naturalHeight}));
  main.querySelectorAll('[style*="background-image"]').forEach(e => {
    const m = /url\(["']?([^"')]+)/.exec(e.style.backgroundImage || '');
    if (m) img.push({url: ass(m[1]), alt: 'sfondo', w: 9999, h: 9999});
  });
  return {titolo: document.title, html: main.outerHTML, link, embed, img};
}"""


def slug(url):
    p = urllib.parse.urlparse(url).path.replace("/view/makebookagente", "").strip("/")
    return urllib.parse.unquote(p).replace("/", "__") or "home"


def pulisci(url):
    u = urllib.parse.urlparse(url)
    return urllib.parse.urlunparse((u.scheme, u.netloc, u.path.rstrip("/"), "", "", ""))


def tipo(url):
    for chiave, nome in (("youtube.com", "video"), ("youtu.be", "video"), ("drive.google.com", "drive"),
                         ("docs.google.com", "documento"), ("makwheels", "mak"), (".pdf", "pdf")):
        if chiave in url:
            return nome
    return "esterno"


def markdown(frammento, immagini):
    c = re.sub(r"<(script|style|svg|noscript|form|iframe)\b.*?</\1>", "", frammento, flags=re.S)
    for url, nome in immagini.items():
        c = c.replace(url.replace("&", "&amp;"), "../immagini/" + nome).replace(url, "../immagini/" + nome)
    c = re.sub(r'href="https?://www\.google\.com/url\?q=([^"&]+)[^"]*"',
               lambda m: 'href="%s"' % urllib.parse.unquote(m.group(1)), c)
    c = re.sub(r'\s(srcset|sizes|style|class|id|data-[a-z_-]+|jsname|jscontroller|jsaction|jsmodel|role|tabindex|dir|aria-[a-z]+)="[^"]*"', "", c)
    out = subprocess.run(["pandoc", "-f", "html", "-t", "gfm-raw_html", "--wrap=none"],
                         input=c, capture_output=True, text=True, check=True).stdout
    return re.sub(r"\n{3,}", "\n\n", out).strip() + "\n"


def aspetta_login(browser):
    fine = time.time() + ATTESA_LOGIN
    while time.time() < fine:
        for ctx in browser.contexts:
            for p in ctx.pages:
                if p.url.startswith(BASE):
                    return ctx
        # non time.sleep: bloccherebbe gli eventi di Playwright e gli URL resterebbero fermi
        pagine = [p for ctx in browser.contexts for p in ctx.pages]
        pagine[0].wait_for_timeout(5000) if pagine else time.sleep(5)
    sys.exit("Login non completato entro il tempo massimo: nessuna pagina del sito aperta.")


def sessione(ctx):
    """Opener urllib con i cookie Google del Chrome in cui hai fatto il login (per le immagini)."""
    vaso = http.cookiejar.CookieJar()
    for c in ctx.cookies():
        if "google" in c["domain"]:
            vaso.set_cookie(http.cookiejar.Cookie(
                0, c["name"], c["value"], None, False, c["domain"], True, c["domain"].startswith("."),
                c["path"], True, c["secure"], None, False, None, None, {}))
    web = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(vaso))
    web.addheaders = [("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                                     "(KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36")]
    return web


def leggi(page, url):
    page.goto(url, wait_until="domcontentloaded", timeout=90000)
    try:
        page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        pass
    if not page.url.startswith(BASE):
        return {"url": page.url}
    # scorre fino in fondo per far caricare immagini e incorporamenti pigri
    for _ in range(25):
        page.mouse.wheel(0, 2500)
        page.wait_for_timeout(100)
    page.wait_for_timeout(1000)
    d = page.evaluate(ESTRAI)
    d["url"] = page.url
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pagine", type=int, default=0, help="si ferma dopo N pagine (per le prove)")
    massimo = ap.parse_args().max_pagine
    for d in (PAGINE, IMMAGINI) + ((GREZZI,) if GREZZI else ()):
        os.makedirs(d, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(CDP)
        ctx = aspetta_login(browser)
        web = sessione(ctx)
        page = ctx.new_page()
        coda, viste, righe, immagini = [BASE + "/home-page"], set(), [], {}
        while coda:
            if massimo and len(viste) >= massimo:
                print("Fermato dopo %d pagine (--max-pagine)." % massimo)
                break
            url = pulisci(coda.pop(0))
            if url in viste:
                continue
            viste.add(url)
            # se la scheda viene chiusa o va in crash a metà pagina, la riapre e riprova;
            # con EBOOK_GREZZI le pagine già lette restano in cache e un rilancio riparte da lì
            cache = os.path.join(GREZZI, slug(url) + ".json") if GREZZI else None
            d = None
            if cache and os.path.exists(cache):
                with open(cache, encoding="utf-8") as f:
                    d = json.load(f)
            for tentativo in range(4):
                if d:
                    break
                try:
                    if page.is_closed():
                        page = ctx.new_page()
                    d = leggi(page, url)
                except Exception as e:
                    print("  riprovo %s: %s" % (url, str(e).splitlines()[0][:80]), flush=True)
            if not d:
                print("NON SCARICATA:", url, flush=True)
                continue
            if not d["url"].startswith(BASE):
                print("SALTATA (redirect fuori dal sito):", url, "->", d["url"][:80], flush=True)
                continue
            if cache and not os.path.exists(cache):
                with open(cache, "w", encoding="utf-8") as f:
                    json.dump(d, f)
            viste.add(pulisci(d["url"]))
            nome = slug(d["url"])
            for i in d["img"]:
                u = i["url"]
                if not u.startswith("http") or u in immagini or min(i["w"], i["h"]) < 120:
                    continue
                prefisso = "%s-%s" % (nome[:40], hashlib.md5(u.encode()).hexdigest()[:8])
                gia = [x for x in os.listdir(IMMAGINI) if x.startswith(prefisso + ".")]
                if gia:
                    immagini[u] = gia[0]
                    continue
                try:
                    # non ctx.request: con Chrome recenti rompe la connessione per gli script successivi
                    with web.open(u, timeout=60) as r:
                        est = {"image/png": ".png", "image/gif": ".gif", "image/webp": ".webp"}.get(
                            r.headers.get("content-type", "").split(";")[0], ".jpg")
                        corpo_img = r.read()
                    file = prefisso + est
                    with open(os.path.join(IMMAGINI, file), "wb") as f:
                        f.write(corpo_img)
                    immagini[u] = file
                except Exception as e:
                    print("  immagine non scaricata:", u[:80], e)
            esterni = []
            for l in d["link"] + d["embed"]:
                u = l["url"]
                if not u.startswith("http"):
                    continue
                if pulisci(u).startswith(BASE):
                    if pulisci(u) not in viste:
                        coda.append(u)
                    continue
                if l.get("nav") or "accounts.google.com" in u or "/reportabuse" in u.lower():
                    continue
                if (u, l["testo"]) not in esterni:
                    esterni.append((u, l["testo"]))
                    righe.append([nome, tipo(u), l["testo"].replace("\n", " ")[:150], u])
            with open(os.path.join(PAGINE, nome + ".md"), "w", encoding="utf-8") as f:
                f.write("# %s\n\nFonte: %s\n\n" % (d["titolo"], d["url"]))
                f.write(markdown(d["html"], immagini))
                if esterni:
                    f.write("\n## Collegamenti e incorporamenti\n\n")
                    f.writelines("- [%s] %s — %s\n" % (tipo(u), t.replace("\n", " ") or "(senza testo)", u) for u, t in esterni)
            print("OK %-50s link %3d  immagini %3d" % (nome, len(esterni), len(d["img"])), flush=True)
        if not page.is_closed():
            page.close()
    with open(os.path.join(RADICE, "collegamenti.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["pagina", "tipo", "testo", "url"])
        w.writerows(righe)
    print("Pagine: %d  collegamenti: %d  immagini: %d" % (len(os.listdir(PAGINE)), len(righe), len(immagini)))


if __name__ == "__main__":
    main()
