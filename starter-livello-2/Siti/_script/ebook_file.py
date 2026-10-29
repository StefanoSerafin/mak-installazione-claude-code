#!/usr/bin/env python3
"""Scarica in Siti/EBOOK/download/<pagina>/ i file Google Drive e Documenti collegati dalle pagine
del sito agenti (elenco in Siti/EBOOK/collegamenti.csv, scritto da ebook_pagine.py) e scrive
Siti/EBOOK/file.csv con l'esito di ogni file.

Usa lo stesso Chrome in cui hai fatto il login (vedi ebook_pagine.py).
I video e i file oltre MAX_MB non si scaricano: restano elencati in file.csv con il loro link.
I file già scaricati non vengono riscaricati: se si interrompe, si rilancia.
MATERIALE RISERVATO AGLI AGENTI MAK: resta su questo computer, mai su GitHub."""
import csv, http.cookiejar, os, re, shutil, urllib.error, urllib.parse, urllib.request

from playwright.sync_api import sync_playwright

CDP = "http://127.0.0.1:9333"
MAX_MB = 50  # oltre questa dimensione il file viene solo elencato
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36")
QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.join(QUI, "..", "EBOOK")
DOWNLOAD = os.path.join(RADICE, "download")
ESPORTA = {"document": "pdf", "presentation": "pdf", "spreadsheets": "xlsx"}


def sorgente(url):
    """(id, url di download, tipo) per i link scaricabili; None per cartelle, moduli e resto."""
    m = re.search(r"docs\.google\.com/(document|presentation|spreadsheets)/d/([\w-]+)", url)
    if m:
        fmt = ESPORTA[m.group(1)]
        return m.group(2), "https://docs.google.com/%s/d/%s/export?format=%s" % (m.group(1), m.group(2), fmt), m.group(1)
    m = re.search(r"drive\.google\.com/(?:file/d/|open\?id=|uc\?.*?id=)([\w-]+)", url)
    if m:
        return m.group(1), "https://drive.usercontent.google.com/download?id=%s&export=download&confirm=t" % m.group(1), "file"
    return None


def nome_file(intestazioni, ripiego):
    cd = intestazioni.get("content-disposition", "")
    m = re.search(r"filename\*=UTF-8''([^;]+)", cd) or re.search(r'filename="([^"]+)"', cd)
    nome = urllib.parse.unquote(m.group(1)) if m else ripiego
    return re.sub(r'[/\\:*?"<>|]', "_", nome).strip()


def sessione():
    """Opener urllib con i cookie Google del Chrome autenticato: il download vero non passa da
    Playwright (la connessione CDP cade dopo qualche decina di file e tiene tutto in memoria)."""
    with sync_playwright() as pw:
        cookie = pw.chromium.connect_over_cdp(CDP).contexts[0].cookies()
    vaso = http.cookiejar.CookieJar()
    for c in cookie:
        if "google" in c["domain"]:
            vaso.set_cookie(http.cookiejar.Cookie(
                0, c["name"], c["value"], None, False, c["domain"], True, c["domain"].startswith("."),
                c["path"], True, c["secure"], None, False, None, None, {}))
    web = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(vaso))
    web.addheaders = [("User-Agent", UA)]
    return web


def apri(web, url):
    """Apre il download; sui file grossi Drive risponde con l'avviso "scansione antivirus non
    possibile", un modulo con campi nascosti (uuid, at) da rimandare per avere il file."""
    r = web.open(url, timeout=120)
    if "text/html" in r.headers.get("content-type", ""):
        campi = dict(re.findall(r'name="(\w+)" value="([^"]*)"', r.read().decode("utf-8", "replace")))
        r.close()
        if "uuid" in campi:
            return web.open("https://drive.usercontent.google.com/download?" + urllib.parse.urlencode(campi), timeout=120)
        return web.open(url, timeout=120)
    return r


def main():
    with open(os.path.join(RADICE, "collegamenti.csv"), encoding="utf-8-sig", newline="") as f:
        link = list(csv.DictReader(f, delimiter=";"))
    # ripresa: i file già scaricati in un giro precedente non vengono richiesti di nuovo
    fatti = {}
    if os.path.exists(os.path.join(RADICE, "file.csv")):
        with open(os.path.join(RADICE, "file.csv"), encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f, delimiter=";"):
                if r["esito"].startswith("download/") and os.path.exists(os.path.join(RADICE, r["esito"])):
                    fatti[r["id_drive"]] = [r["tipo"], r["nome_file"], r["mb"], r["esito"], r["url"]]
    web, righe = sessione(), []
    for l in link:
        s = sorgente(l["url"])
        if not s:
            continue
        fid, url, tipo = s
        if fid in fatti:  # stesso file collegato da più pagine: una sola copia
            righe.append([l["pagina"], fid] + fatti[fid])
            continue
        try:
            with apri(web, url) as r:
                h = r.headers
                if "text/html" in h.get("content-type", ""):
                    esito = [tipo, "", "", "NON ACCESSIBILE (pagina HTML al posto del file)", l["url"]]
                else:
                    mb = int(h.get("content-length") or 0) / 1e6
                    nome = nome_file(h, fid)
                    rel = os.path.join(l["pagina"], nome)
                    dest = os.path.join(DOWNLOAD, rel)
                    if h.get("content-type", "").startswith("video/") or re.search(r"\.(mp4|mov|m4v|avi|webm)$", nome, re.I):
                        esito = [tipo, nome, "%.1f" % mb, "SOLO ELENCATO (video)", l["url"]]
                    elif mb > MAX_MB:
                        esito = [tipo, nome, "%.1f" % mb, "SOLO ELENCATO (oltre %d MB)" % MAX_MB, l["url"]]
                    else:
                        os.makedirs(os.path.dirname(dest), exist_ok=True)
                        with open(dest + ".part", "wb") as f:
                            shutil.copyfileobj(r, f, 1 << 20)
                        os.replace(dest + ".part", dest)
                        esito = [tipo, nome, "%.1f" % (os.path.getsize(dest) / 1e6), "download/" + rel, l["url"]]
        except urllib.error.HTTPError as e:
            esito = [tipo, "", "", "NON ACCESSIBILE (%d)" % e.code, l["url"]]
        except Exception as e:
            esito = [tipo, "", "", "ERRORE: %s" % str(e).splitlines()[0][:120], l["url"]]
        fatti[fid] = esito
        righe.append([l["pagina"], fid] + esito)
        print("%-45s %-40s %s" % (l["pagina"][:45], esito[1][:40], esito[3][:60]), flush=True)
    with open(os.path.join(RADICE, "file.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["pagina", "id_drive", "tipo", "nome_file", "mb", "esito", "url"])
        w.writerows(righe)
    ok = [e for e in fatti.values() if e[3].startswith("download/")]
    print("File distinti: %d  scaricati: %d (%.0f MB)  non scaricati: %d" % (
        len(fatti), len(ok), sum(float(e[2]) for e in ok), len(fatti) - len(ok)))


if __name__ == "__main__":
    main()
