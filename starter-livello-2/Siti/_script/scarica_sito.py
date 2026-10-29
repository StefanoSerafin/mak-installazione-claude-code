#!/usr/bin/env python3
"""Copia un sito pubblico (WordPress o simile) dentro Siti/<CARTELLA>/ leggendo la sua sitemap.

    python3 Siti/_script/scarica_sito.py --sito https://makwheels.it --cartella MAK
    python3 Siti/_script/scarica_sito.py --sito https://makwheels.it --cartella MAK --conta
    python3 Siti/_script/scarica_sito.py --sito https://noproblemkit.com --cartella NPK --escludi "ground_catalog|antifurti"

Cosa produce in Siti/<CARTELLA>/:
  <tipo>/<pagina>.md   una pagina = un file Markdown (pagine/, articoli/, prodotti/, promozioni/...),
                       con titolo, indirizzo, data e il testo della pagina
  download/            PDF, Excel, Word e zip collegati dalle pagine
  video.md             titolo della pagina e link di ogni video YouTube o Vimeo trovato
  indice.csv           una riga per pagina e per documento (separatore ;, si apre in Numbers/Excel)

--conta     dice solo quante pagine ci sono, senza scaricare niente
--aggiorna  riscarica anche le pagine già presenti (senza, un rilancio riparte da dove si era fermato)
--tipi prodotti,pagine   copia solo questi tipi (i nomi sono quelli stampati da --conta)
--max-pagine N   si ferma dopo N pagine (per le prove)

Scarica con calma: una richiesta alla volta, con una pausa. Richiede pandoc (installato nel livello 1)."""
import argparse, csv, hashlib, html, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import date

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.0 Safari/605.1.15")
QUI = os.path.dirname(os.path.abspath(__file__))
SITI = os.path.join(QUI, "..")
PAUSA = 1.0
# sitemap di sole etichette (categorie, autori, attributi): non hanno contenuto proprio
TASSONOMIE = r"category|categoria|author|tag|pa_|product_cat|product_tag|post_format|elementor"
NOMI = {"page": "pagine", "post": "articoli", "product": "prodotti", "promozione": "promozioni"}
DOCUMENTI = r"\.(?:pdf|xlsx?|docx?|pptx?|zip)(?:\?[^\"'#]*)?$"
VIDEO = (r"https?://(?:www\.)?(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/|"
         r"player\.vimeo\.com/video/|vimeo\.com/)[\w-]+")


def get(url, binario=False):
    time.sleep(PAUSA)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for tentativo in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                dati = r.read()
            return dati if binario else dati.decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                sys.exit(f"Il sito ha risposto {e.code} su {url}: probabilmente ci sta limitando. "
                         "Fermati e riprova più tardi (il rilancio riparte da dove si era fermato).")
            if e.code == 404 or tentativo == 2:
                raise
        except Exception:
            if tentativo == 2:
                raise
        time.sleep(5 * (tentativo + 1))


def sitemap(sito, salta):
    """Elenco (sitemap, tipo, url) delle pagine, partendo dall'indice; le sitemap che
    corrispondono a salta non si scaricano nemmeno. Ritorna anche quante sono state saltate."""
    for nome in ("sitemap_index.xml", "wp-sitemap.xml", "sitemap.xml"):
        try:
            indice = get(f"{sito}/{nome}")
            break
        except Exception:
            indice = None
    if not indice:
        sys.exit(f"{sito} non ha una sitemap leggibile: serve un altro metodo (chiedi a Claude).")
    figlie = re.findall(r"<sitemap>\s*<loc>([^<]+)</loc>", indice)
    if not figlie:  # la sitemap è già l'elenco delle pagine
        figlie = [None]
    out, saltate = [], []
    for f in figlie:
        if f and re.search(salta, f.rsplit("/", 1)[-1]):
            saltate.append(f.rsplit("/", 1)[-1])
            continue
        testo = indice if f is None else get(html.unescape(f))
        m = re.search(r"/(?:wp-sitemap-posts-)?([\w-]+?)(?:-sitemap\d*|-\d+)?\.xml", f or "")
        tipo = m.group(1) if m else "page"
        for u in re.findall(r"<url>\s*<loc>([^<]+)</loc>", testo):
            out.append((f or "", tipo, html.unescape(u).strip()))
    return out, saltate


def meta(pagina, nome):
    m = re.search(r'<meta[^>]*(?:name|property)="%s"[^>]*content="([^"]*)"' % nome, pagina)
    return html.unescape(m.group(1)).strip() if m else ""


def corpo(pagina):
    """Solo il contenuto della pagina, senza menu, piè di pagina, script e moduli."""
    for inizio in (r"<main\b", r'<div data-elementor-type="(?:wp-page|wp-post|single-post|product|single-page)"',
                   r"<article\b", r"<body\b"):
        m = re.search(inizio, pagina)
        if m:
            break
    fine = len(pagina)
    for f in (r'<footer data-elementor-type="footer"', r'<div data-elementor-type="footer"', r"<footer\b"):
        n = re.search(f, pagina[m.start():] if m else pagina)
        if n:
            fine = (m.start() if m else 0) + n.start()
            break
    c = pagina[m.start() if m else 0:fine]
    c = re.sub(r"<(script|style|svg|noscript|form|select|iframe|nav|header|button)\b.*?</\1>", "", c, flags=re.S)
    c = re.sub(r"<!--.*?-->", "", c, flags=re.S)
    c = re.sub(r'\s(srcset|sizes|style|class|id|data-[\w-]+|decoding|loading|width|height|aria-[\w-]+|role)="[^"]*"', "", c)
    c = re.sub(r'<img[^>]*src="data:[^"]*"[^>]*>', "", c)
    return c


def markdown(frammento):
    out = subprocess.run(["pandoc", "-f", "html", "-t", "gfm-raw_html", "--wrap=none"],
                         input=frammento, capture_output=True, text=True, check=True).stdout
    out = re.sub(r"\[([^\]]*)\]\(#[^)]*\)", r"\1", out)  # pulsanti interni (apri/chiudi finestre)
    out = re.sub(r"^\s*\[\s*\]\([^)]*\)\s*$", "", out, flags=re.M)  # link senza testo
    out = "\n".join(r.rstrip() for r in out.splitlines())
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip() + "\n"


def nome_pagina(sito, url):
    p = urllib.parse.unquote(urllib.parse.urlparse(url).path).strip("/")
    nome = re.sub(r'[\\:*?"<>|]', "_", p.replace("/", "__")) or "home"
    return nome[:150]


def main():
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("--sito", required=True, help="indirizzo, es. https://makwheels.it")
    a.add_argument("--cartella", required=True, help="nome della cartella dentro Siti/, es. MAK")
    a.add_argument("--escludi", default="", help="sitemap da saltare (espressione regolare sul nome)")
    a.add_argument("--tipi", default="", help="solo questi tipi, separati da virgola, es. prodotti,pagine")
    a.add_argument("--max-pagine", type=int, default=0)
    a.add_argument("--conta", action="store_true")
    a.add_argument("--aggiorna", action="store_true")
    arg = a.parse_args()
    sito = arg.sito.rstrip("/")
    radice = os.path.join(SITI, arg.cartella)

    salta = TASSONOMIE + ("|" + arg.escludi if arg.escludi else "")
    tutte, sitemap_saltate = sitemap(sito, salta)
    pagine = [(t, u) for f, t, u in tutte if not re.search(r"\.(jpe?g|png|webp|gif|svg)$", u, re.I)]
    conteggio = {}
    for t, _ in pagine:
        conteggio[NOMI.get(t, t)] = conteggio.get(NOMI.get(t, t), 0) + 1
    print(f"{sito}: {len(pagine)} pagine da copiare ({', '.join(f'{k} {v}' for k, v in sorted(conteggio.items()))})")
    if sitemap_saltate:
        print("  sitemap saltate (categorie, attributi, esclusioni): " + ", ".join(sitemap_saltate))
    if arg.conta:
        return
    if arg.tipi:
        voluti = {t.strip() for t in arg.tipi.split(",")}
        pagine = [(t, u) for t, u in pagine if NOMI.get(t, t) in voluti]
    if arg.max_pagine:
        pagine = pagine[:arg.max_pagine]

    os.makedirs(os.path.join(radice, "download"), exist_ok=True)
    righe, documenti, video = [], {}, []
    fatte = nuove = 0
    for tipo, url in pagine:
        cartella = NOMI.get(tipo, tipo)
        nome = nome_pagina(sito, url)
        dest = os.path.join(radice, cartella, nome + ".md")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            if os.path.exists(dest) and not arg.aggiorna:
                pagina = None
                with open(dest, encoding="utf-8") as f:
                    testo = f.read()
                titolo = (re.match(r"# (.*)", testo) or [None, nome])[1]
                link_doc = re.findall(r"^- Documento: (\S+)", testo, re.M)
                link_video = re.findall(r"^- Video: (\S+)", testo, re.M)
            else:
                pagina = get(url)
                grezza = html.unescape(pagina).replace("\\/", "/")
                tit = re.search(r"<title[^>]*>(.*?)</title>", pagina, re.S)
                titolo = re.sub(r"\s+", " ", html.unescape(tit.group(1))).strip() if tit else nome
                link_video = sorted(set(re.findall(VIDEO, grezza)))
                link_doc = sorted({urllib.parse.urljoin(url, h) for h in re.findall(r'href="([^"]+)"', grezza)
                                   if re.search(DOCUMENTI, h, re.I)})
                testa = [f"# {titolo}", "", f"- URL: {url}", f"- Copiata il: {date.today().isoformat()}"]
                if meta(pagina, "description"):
                    testa.append(f"- Descrizione: {meta(pagina, 'description')}")
                if meta(pagina, "article:modified_time"):
                    testa.append(f"- Ultima modifica sul sito: {meta(pagina, 'article:modified_time')[:10]}")
                testa += [f"- Documento: {d}" for d in link_doc] + [f"- Video: {v}" for v in link_video]
                with open(dest, "w", encoding="utf-8") as f:
                    f.write("\n".join(testa) + "\n\n---\n\n" + markdown(corpo(pagina)))
                nuove += 1
            fatte += 1
            for d in link_doc:
                documenti.setdefault(d, []).append(f"{cartella}/{nome}")
            for v in link_video:
                video.append((titolo, f"{cartella}/{nome}", v))
            righe.append(["pagina", cartella, titolo, url, f"{cartella}/{nome}.md"])
            print(f"{fatte:4}/{len(pagine)}  {cartella}/{nome}", flush=True)
        except Exception as e:
            righe.append(["pagina", cartella, "", url, f"NON SCARICATA: {str(e)[:100]}"])
            print(f"NON SCARICATA {url}: {e}", flush=True)

    for d, da in sorted(documenti.items()):
        base = urllib.parse.unquote(os.path.basename(urllib.parse.urlparse(d).path)) or "documento"
        base = re.sub(r'[\\/:*?"<>|]', "_", base)
        file = os.path.join(radice, "download", base)
        if os.path.exists(file) and not arg.aggiorna:
            esito = f"download/{base}"
        else:
            try:
                dati = get(d, binario=True)
                with open(file, "wb") as f:
                    f.write(dati)
                esito = f"download/{base}"
                print("documento", base, flush=True)
            except Exception as e:
                esito = f"NON SCARICATO: {str(e)[:100]}"
                print("DOCUMENTO NON SCARICATO", d, e, flush=True)
        righe.append(["documento", "download", base, d, esito + "  (da " + ", ".join(sorted(set(da))[:5]) + ")"])

    with open(os.path.join(radice, "video.md"), "w", encoding="utf-8") as f:
        f.write(f"# Video trovati su {sito}\n\nCopiato il {date.today().isoformat()}. I video non si scaricano: qui c'è solo il link.\n\n")
        visti = set()
        for titolo, pag, v in video:
            if v not in visti:
                visti.add(v)
                f.write(f"- {v} — {titolo} ({pag})\n")
    with open(os.path.join(radice, "indice.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["cosa", "cartella", "titolo", "url", "file"])
        w.writerows(righe)
    nd = sum(1 for r in righe if r[0] == "documento" and r[4].startswith("download/"))
    print(f"\nFatto: {fatte} pagine ({nuove} nuove), {nd} documenti su {len(documenti)}, {len(set(v for *_, v in video))} video. "
          f"Ora estrai il testo dei documenti:  python3 Siti/_script/estrai_testo.py --cartella {arg.cartella}")


if __name__ == "__main__":
    main()
